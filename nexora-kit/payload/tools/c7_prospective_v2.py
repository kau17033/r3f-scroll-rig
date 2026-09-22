#!/usr/bin/env python3
"""C7 v2 preregistered prospective ORP/Controller evaluation.

The plan is frozen in control/C7-PROSPECTIVE-PLAN-v2.json. This runner does
not change task templates, query generation, policy translation, objective, or
decision rule based on observed outcomes.
"""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import math
import os
import sys
import time
from urllib.request import Request, urlopen

from dream_replay import INCUMBENT, improve_policy, load_world

ROOT=os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
PLAN_PATH=os.path.join(ROOT,"control","C7-PROSPECTIVE-PLAN-v2.json")
WORLD_PATH=os.path.join(ROOT,"control","replay_worlds","bootstrap_convergence_20260922.json")

def fetch_text(repo,ref,path):
    url="https://raw.githubusercontent.com/%s/%s/%s" % (repo,ref,path)
    last=None
    for i in range(4):
        try:
            req=Request(url,headers={
                "User-Agent":"NEXORA-C7-v2/1.0",
                "Cache-Control":"no-cache",
            })
            t0=time.perf_counter()
            with urlopen(req,timeout=25) as r:
                body=r.read().decode("utf-8")
            return body,time.perf_counter()-t0
        except Exception as exc:
            last=exc
            time.sleep(0.5*(i+1))
    raise RuntimeError("fetch failed %s: %r" % (url,last))

def sha_key(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def candidate_order(task):
    return sorted(task["candidates"],key=lambda p:sha_key(task["task_id"]+"|"+p))

def _eligible_line(line):
    s=line.strip()
    if not (20 <= len(s) <= 160):
        return None
    if not s or s.startswith("#") or s.startswith("import ") or s.startswith("from "):
        return None
    return s

def generate_query(task,bodies):
    """Evaluator-only deterministic benchmark-label construction."""
    unique={}
    for path,body in bodies.items():
        for raw in body.splitlines():
            line=_eligible_line(raw)
            if line is None:
                continue
            if line in unique:
                continue
            hits=[p for p,b in bodies.items() if line in b]
            if len(hits)==1:
                unique[line]=hits[0]
    if not unique:
        raise RuntimeError("no unique eligible query for %s" % task["task_id"])
    line=min(unique,key=lambda x:sha_key(task["task_id"]+"|"+x))
    return line,unique[line],len(unique)

def setup_task(task):
    bodies={}
    request_seconds=0.0
    for p in task["candidates"]:
        body,sec=fetch_text(task["repo"],task["ref"],p)
        bodies[p]=body
        request_seconds+=sec
    query,target_path,eligible_count=generate_query(task,bodies)
    # Verify live observation semantics: exact substring must be in exactly one candidate.
    hits=[p for p,b in bodies.items() if query in b]
    if hits != [target_path]:
        raise RuntimeError("query uniqueness invariant failed for %s: %r" % (task["task_id"],hits))
    return {
        "query":query,
        "target_path":target_path,
        "eligible_unique_lines":eligible_count,
        "setup_probes":len(task["candidates"]),
        "setup_request_seconds":request_seconds,
    }

def batch_size(policy,max_parallelism):
    return max(1,min(max_parallelism,int(math.ceil(max_parallelism*float(policy["batch_fraction"])))))

def rollout(task,query,policy,max_parallelism):
    order=candidate_order(task)
    bs=batch_size(policy,max_parallelism)
    probes=0
    rounds=0
    elapsed=0.0
    observations=[]
    found=[]
    for start in range(0,len(order),bs):
        batch=order[start:start+bs]
        rounds+=1
        t0=time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch)) as ex:
            futures=[(p,ex.submit(fetch_text,task["repo"],task["ref"],p)) for p in batch]
            batch_obs=[]
            for p,fut in futures:
                body,request_sec=fut.result()
                hit=query in body
                batch_obs.append({"path":p,"hit":hit,"request_seconds":request_sec})
        elapsed+=time.perf_counter()-t0
        probes+=len(batch)
        batch_obs.sort(key=lambda x:order.index(x["path"]))
        observations.extend(batch_obs)
        found.extend(x["path"] for x in batch_obs if x["hit"])
        if found:
            break
    resolved=len(found)==1
    ig=2.0 if resolved else 0.0
    utility=ig-0.25*probes-0.05*rounds-0.02*elapsed
    return {
        "policy_id":policy["policy_id"],
        "batch_fraction":policy["batch_fraction"],
        "batch_size":bs,
        "candidate_order":order,
        "probes":probes,
        "decision_rounds":rounds,
        "latency_seconds":elapsed,
        "resolved":resolved,
        "found_paths":found,
        "information_gain_bits":ig,
        "utility":utility,
        "observations":observations,
    }

def mean(xs):
    return sum(xs)/len(xs) if xs else None

def main():
    with open(PLAN_PATH,encoding="utf-8") as f:
        plan=json.load(f)
    if plan.get("status")!="FROZEN_BEFORE_V2_LIVE_OUTCOMES":
        raise RuntimeError("plan not frozen")

    historical=improve_policy(load_world(WORLD_PATH))
    selected=historical["selected"]["policy"]
    baseline=dict(INCUMBENT)
    expected_id=plan["policy_source"]["expected_selected_policy_id"]
    if selected["policy_id"]!=expected_id:
        raise RuntimeError("historical selected policy drift: %s != %s" % (selected["policy_id"],expected_id))

    maxp=int(plan["live_interface"]["max_parallelism"])
    prediction={
        "historical_world":historical["world_id"],
        "selected_policy":selected,
        "baseline_policy":baseline,
        "replay_incumbent_reward":historical["incumbent"]["result"]["reward"],
        "replay_selected_reward":historical["selected"]["result"]["reward"],
        "replay_predicted_reward_gain":historical["selected"]["result"]["reward"]-historical["incumbent"]["result"]["reward"],
        "predicted_information_gain_bits_per_valid_task":2.0,
        "baseline_batch_size":batch_size(baseline,maxp),
        "dream_batch_size":batch_size(selected,maxp),
        "pre_live_cost_hypothesis":"Dream batch size is smaller; expected probe cost is lower when the unique target is reached before the final candidate.",
    }

    rows=[]
    invalid=[]
    for task in plan["tasks"]:
        try:
            setup=setup_task(task)
        except Exception as exc:
            invalid.append(task["task_id"])
            rows.append({"task_id":task["task_id"],"repo":task["repo"],"ref":task["ref"],"valid":False,"setup_error":repr(exc)})
            continue

        even=int(sha_key(task["task_id"])[0],16)%2==0
        if even:
            first_name,first_policy="baseline",baseline
            second_name,second_policy="dream",selected
        else:
            first_name,first_policy="dream",selected
            second_name,second_policy="baseline",baseline

        first=rollout(task,setup["query"],first_policy,maxp)
        second=rollout(task,setup["query"],second_policy,maxp)
        result_by_name={first_name:first,second_name:second}

        # Post-run validity check uses evaluator setup truth, never policy observations.
        valid=(
            result_by_name["baseline"]["resolved"]
            and result_by_name["dream"]["resolved"]
            and result_by_name["baseline"]["found_paths"]==[setup["target_path"]]
            and result_by_name["dream"]["found_paths"]==[setup["target_path"]]
        )
        if not valid:
            invalid.append(task["task_id"])
        rows.append({
            "task_id":task["task_id"],
            "repo":task["repo"],
            "ref":task["ref"],
            "valid":valid,
            "run_order":[first_name,second_name],
            "setup":setup,
            "baseline":result_by_name["baseline"],
            "dream":result_by_name["dream"],
        })

    valid_rows=[r for r in rows if r.get("valid")]
    min_valid=int(plan["decision_rule"]["minimum_valid_tasks"])
    b_res=mean([1.0 if r["baseline"]["resolved"] else 0.0 for r in valid_rows])
    d_res=mean([1.0 if r["dream"]["resolved"] else 0.0 for r in valid_rows])
    b_util=mean([r["baseline"]["utility"] for r in valid_rows])
    d_util=mean([r["dream"]["utility"] for r in valid_rows])
    b_probes=sum(r["baseline"]["probes"] for r in valid_rows)
    d_probes=sum(r["dream"]["probes"] for r in valid_rows)
    closure=(
        len(valid_rows)>=min_valid
        and len(valid_rows)==len(plan["tasks"])
        and not invalid
        and b_res==1.0
        and d_res==1.0
    )
    improved=(
        closure
        and d_util is not None and b_util is not None
        and d_util>b_util
        and d_probes<=b_probes
        and d_res>=b_res
    )
    summary={
        "valid_tasks":len(valid_rows),
        "invalid_tasks":invalid,
        "baseline_resolution_rate":b_res,
        "dream_resolution_rate":d_res,
        "baseline_mean_utility":b_util,
        "dream_mean_utility":d_util,
        "mean_utility_difference":(d_util-b_util) if closure else None,
        "baseline_total_probes":b_probes,
        "dream_total_probes":d_probes,
        "probe_difference":d_probes-b_probes,
        "evaluation_closure":closure,
        "controller_improved":improved,
        "controller_result":"IMPROVED" if improved else ("NO_IMPROVEMENT" if closure else "INVALID_OR_INCOMPLETE"),
    }
    out={
        "schema":"nexora-c7-prospective-result/2.0",
        "plan":"control/C7-PROSPECTIVE-PLAN-v2.json",
        "plan_status":plan["status"],
        "prediction":prediction,
        "tasks":rows,
        "summary":summary,
        "claim_ceiling":plan["claim_ceiling"],
    }
    print(json.dumps(out,sort_keys=True,indent=2))
    return 0 if closure else 2

if __name__=="__main__":
    sys.exit(main())

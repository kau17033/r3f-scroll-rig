#!/usr/bin/env python3
"""C7 prospective live evaluation of ORP/Controller vs locked baseline."""
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
PLAN_PATH=os.path.join(ROOT,"control","C7-PROSPECTIVE-PLAN-v1.json")
WORLD_PATH=os.path.join(ROOT,"control","replay_worlds","bootstrap_convergence_20260922.json")

def get_text(repo,ref,path):
    url="https://raw.githubusercontent.com/%s/%s/%s" % (repo,ref,path)
    last=None
    for i in range(4):
        try:
            req=Request(url,headers={"User-Agent":"NEXORA-C7-prospective/1.0","Cache-Control":"no-cache"})
            t=time.perf_counter()
            with urlopen(req,timeout=25) as r:
                body=r.read().decode("utf-8")
            return body,time.perf_counter()-t
        except Exception as exc:
            last=exc
            time.sleep(0.5*(i+1))
    raise RuntimeError("fetch failed %s: %r" % (url,last))

def ordered_candidates(task):
    return sorted(task["candidates"],key=lambda p:hashlib.sha256((task["task_id"]+"|"+p).encode()).hexdigest())

def batch_size(policy,max_parallelism):
    return max(1,min(max_parallelism,int(math.ceil(max_parallelism*float(policy["batch_fraction"])))))

def rollout(task,policy,max_parallelism):
    order=ordered_candidates(task)
    bs=batch_size(policy,max_parallelism)
    probes=0
    rounds=0
    elapsed=0.0
    observations=[]
    found=[]
    for start in range(0,len(order),bs):
        batch=order[start:start+bs]
        rounds+=1
        wall0=time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch)) as ex:
            futs={ex.submit(get_text,task["repo"],task["ref"],p):p for p in batch}
            batch_obs=[]
            for fut,p in [(f,p) for f,p in futs.items()]:
                body,request_sec=fut.result()
                hit=task["target"] in body
                batch_obs.append({"path":p,"hit":hit,"request_seconds":request_sec})
        wall=time.perf_counter()-wall0
        elapsed+=wall
        probes+=len(batch)
        batch_obs.sort(key=lambda x:order.index(x["path"]))
        observations.extend(batch_obs)
        found.extend(x["path"] for x in batch_obs if x["hit"])
        if found:
            break
    n=len(order)
    resolved=bool(found)
    ig=math.log2(n) if resolved else 0.0
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

def audit_task(task):
    found=[]
    seconds=0.0
    for p in ordered_candidates(task):
        body,sec=get_text(task["repo"],task["ref"],p)
        seconds+=sec
        if task["target"] in body:
            found.append(p)
    return {"target_paths":found,"target_count":len(found),"validation_probes":len(task["candidates"]),"validation_request_seconds":seconds}

def mean(xs):
    return sum(xs)/len(xs) if xs else float("nan")

def main():
    plan=json.load(open(PLAN_PATH,encoding="utf-8"))
    historical=improve_policy(load_world(WORLD_PATH))
    selected=historical["selected"]["policy"]
    baseline=dict(INCUMBENT)
    maxp=int(plan["live_interface"]["max_parallelism"])

    prediction={
        "historical_world":historical["world_id"],
        "selected_policy":selected,
        "baseline_policy":baseline,
        "replay_incumbent_reward":historical["incumbent"]["result"]["reward"],
        "replay_selected_reward":historical["selected"]["result"]["reward"],
        "replay_predicted_reward_gain":historical["selected"]["result"]["reward"]-historical["incumbent"]["result"]["reward"],
        "predicted_ig_bits_per_valid_task":2.0,
        "predicted_cost_direction":"dream<=baseline" if selected["batch_fraction"]<=baseline["batch_fraction"] else "dream>baseline",
    }

    rows=[]
    invalid=[]
    for task in plan["tasks"]:
        # Both live policies start from zero observations and independently issue real HTTP probes.
        b=rollout(task,baseline,maxp)
        d=rollout(task,selected,maxp)
        audit=audit_task(task)
        valid=audit["target_count"]==1
        if not valid:
            invalid.append(task["task_id"])
        rows.append({"task_id":task["task_id"],"repo":task["repo"],"ref":task["ref"],"valid":valid,"audit":audit,"baseline":b,"dream":d})

    valid_rows=[r for r in rows if r["valid"]]
    min_valid=int(plan["decision_rule"]["minimum_valid_tasks"])
    b_res=mean([1.0 if r["baseline"]["resolved"] else 0.0 for r in valid_rows])
    d_res=mean([1.0 if r["dream"]["resolved"] else 0.0 for r in valid_rows])
    b_util=mean([r["baseline"]["utility"] for r in valid_rows])
    d_util=mean([r["dream"]["utility"] for r in valid_rows])
    b_probes=sum(r["baseline"]["probes"] for r in valid_rows)
    d_probes=sum(r["dream"]["probes"] for r in valid_rows)
    closure=len(valid_rows)>=min_valid and not invalid and b_res==1.0 and d_res==1.0
    improved=closure and d_util>b_util and d_probes<=b_probes and d_res>=b_res
    summary={
        "valid_tasks":len(valid_rows),
        "invalid_tasks":invalid,
        "baseline_resolution_rate":b_res,
        "dream_resolution_rate":d_res,
        "baseline_mean_utility":b_util,
        "dream_mean_utility":d_util,
        "mean_utility_difference":d_util-b_util if valid_rows else None,
        "baseline_total_probes":b_probes,
        "dream_total_probes":d_probes,
        "probe_difference":d_probes-b_probes,
        "evaluation_closure":closure,
        "controller_improved":improved,
        "controller_result":"IMPROVED" if improved else ("NO_IMPROVEMENT" if closure else "INVALID_OR_INCOMPLETE"),
    }
    result={
        "schema":"nexora-c7-prospective-result/1.0",
        "plan":"control/C7-PROSPECTIVE-PLAN-v1.json",
        "plan_status":plan["status"],
        "prediction":prediction,
        "tasks":rows,
        "summary":summary,
        "claim_ceiling":plan["claim_ceiling"],
    }
    print(json.dumps(result,sort_keys=True,indent=2))
    # A valid experiment may show NO_IMPROVEMENT and still exit 0.
    return 0 if closure else 2

if __name__=="__main__":
    sys.exit(main())

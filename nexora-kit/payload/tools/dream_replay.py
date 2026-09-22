#!/usr/bin/env python3
"""NEXORA Dream-Replay: prefix-only replay over realized discovery histories.

This is an ORP/Controller engineering component. It never changes scientific gates.
"""
import argparse
import itertools
import json
import math
import os
import sys

ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DEFAULT_WORLD = os.path.join(ROOT, "control", "replay_worlds", "bootstrap_convergence_20260922.json")

INCUMBENT = {
    "policy_id": "fixed_exploration_v0",
    "explore_bias": 1.2,
    "explore_decay": 0.0,
    "success_satiation": 0.0,
    "depth_bias": 0.6,
    "quality_weight": 0.8,
    "evidence_weight": 0.3,
    "recovery_weight": 0.6,
    "risk_penalty": 0.5,
    "depth_penalty": 0.05,
    "stop_threshold": -1.0,
    "batch_fraction": 1.0,
}


def load_world(path):
    with open(path, encoding="utf-8") as f:
        world = json.load(f)
    validate_world(world)
    return world


def validate_world(world):
    nodes = world.get("nodes") or []
    if not nodes:
        raise ValueError("world has no nodes")
    by_id = {}
    created = set()
    for node in nodes:
        nid = node.get("id")
        if not nid or nid in by_id:
            raise ValueError("duplicate/empty node id: %r" % nid)
        by_id[nid] = node
        ci = node.get("created_index")
        if not isinstance(ci, int) or ci in created:
            raise ValueError("created_index must be unique int: %r" % ci)
        created.add(ci)
        for key in ("score", "evidence_gain", "cost", "risk"):
            if not isinstance(node.get(key), (int, float)):
                raise ValueError("%s.%s must be numeric" % (nid, key))

    root = world.get("root_id")
    if root not in by_id or by_id[root].get("parent_id") is not None:
        raise ValueError("invalid root")

    children = {nid: [] for nid in by_id}
    for node in nodes:
        if node["id"] == root:
            continue
        parent = node.get("parent_id")
        if parent not in by_id:
            raise ValueError("%s missing parent %r" % (node["id"], parent))
        children[parent].append(node["id"])
    for parent, ids in children.items():
        ids.sort(key=lambda nid: by_id[nid]["created_index"])
        if parent != root and len(ids) > 1:
            raise ValueError("non-root node %s has >1 recorded child" % parent)

    if int(world.get("max_parallelism", 0)) < 1:
        raise ValueError("max_parallelism must be >=1")
    obj = world.get("objective") or {}
    for key in ("cost_weight", "risk_weight", "parallel_weight"):
        if not isinstance(obj.get(key), (int, float)) or obj[key] < 0:
            raise ValueError("objective.%s must be non-negative number" % key)


def indexes(world):
    by_id = {n["id"]: n for n in world["nodes"]}
    children = {nid: [] for nid in by_id}
    for node in world["nodes"]:
        if node["parent_id"] is not None:
            children[node["parent_id"]].append(node["id"])
    for parent in children:
        children[parent].sort(key=lambda nid: by_id[nid]["created_index"])
    return by_id, children


def legal_actions(world, revealed):
    by_id, children = indexes(world)
    root = world["root_id"]
    actions = []
    if any(child not in revealed for child in children[root]):
        actions.append(root)
    for nid in sorted(revealed, key=lambda x: by_id[x]["created_index"]):
        if nid == root:
            continue
        revealed_child = any(c in revealed for c in children[nid])
        unseen_child = any(c not in revealed for c in children[nid])
        if not revealed_child and unseen_child:
            actions.append(nid)
    return actions


def next_recorded_child(world, parent_id, revealed):
    _, children = indexes(world)
    for child in children[parent_id]:
        if child not in revealed:
            return child
    return None


def depth_of(world, node_id):
    by_id, _ = indexes(world)
    root = world["root_id"]
    depth = 0
    cur = by_id[node_id]
    while cur["parent_id"] is not None and cur["parent_id"] != root:
        depth += 1
        cur = by_id[cur["parent_id"]]
    return depth


def prefix_best(world, revealed):
    by_id, _ = indexes(world)
    vals = [by_id[nid]["score"] for nid in revealed if nid != world["root_id"]]
    return max(vals) if vals else 0.0


def action_priority(world, action_id, revealed, policy):
    by_id, children = indexes(world)
    root = world["root_id"]
    if action_id == root:
        opened_roots = sum(1 for child in children[root] if child in revealed)
        return (
            policy["explore_bias"]
            - policy["explore_decay"] * opened_roots
            - policy["success_satiation"] * prefix_best(world, revealed)
        )

    node = by_id[action_id]
    repair = 1.0 if node["status"] == "failed_repairable" else 0.0
    return (
        policy["depth_bias"]
        + policy["quality_weight"] * node["score"]
        + policy["evidence_weight"] * node["evidence_gain"]
        + policy["recovery_weight"] * repair
        - policy["risk_penalty"] * node["risk"]
        - policy["depth_penalty"] * depth_of(world, action_id)
    )


def select_batch(world, revealed, policy):
    by_id, _ = indexes(world)
    ranked = []
    for action in legal_actions(world, revealed):
        ranked.append((action_priority(world, action, revealed, policy), action))
    ranked.sort(key=lambda x: (-x[0], by_id[x[1]]["created_index"], x[1]))
    if not ranked or ranked[0][0] < policy["stop_threshold"]:
        return []
    cap = max(
        1,
        min(
            int(world["max_parallelism"]),
            int(math.ceil(world["max_parallelism"] * policy["batch_fraction"])),
        ),
    )
    return [action for _, action in ranked[:cap]]


def replay(world, policy):
    validate_world(world)
    by_id, _ = indexes(world)
    revealed = {world["root_id"]}
    order = []
    rounds = 0
    best_history = []

    while True:
        batch = select_batch(world, revealed, policy)
        if not batch:
            break
        newly = []
        for action in batch:
            child = next_recorded_child(world, action, revealed)
            if child is not None:
                newly.append(child)
        if not newly:
            break
        revealed.update(newly)
        order.extend(newly)
        rounds += 1
        best_history.append(prefix_best(world, revealed))
        if len(revealed) == len(by_id):
            break

    nodes = [by_id[nid] for nid in revealed if nid != world["root_id"]]
    best = max((n["score"] for n in nodes), default=0.0)
    work = len(nodes)
    risk = sum(n["risk"] for n in nodes)
    obj = world["objective"]
    reward = (
        best
        - obj["cost_weight"] * work
        - obj["risk_weight"] * risk
        + obj["parallel_weight"] * (work / max(1, rounds))
    )
    return {
        "reward": round(reward, 10),
        "best_score": best,
        "revealed_work": work,
        "decision_rounds": rounds,
        "risk_sum": round(risk, 10),
        "revealed_order": order,
        "best_history": best_history,
    }


def candidate_policies():
    yield dict(INCUMBENT)
    grid = itertools.product(
        (0.6, 1.0, 1.4),       # explore_bias
        (0.05, 0.15, 0.30),    # explore_decay
        (0.0, 0.2),            # success_satiation
        (0.2, 0.6, 1.0),       # depth_bias
        (0.1, 0.5, 1.0),       # evidence_weight
        (0.0, 0.7),            # recovery_weight
        (0.2, 1.0),            # risk_penalty
        (0.3, 0.5, 0.8, 1.1),  # stop_threshold
        (1.0 / 3.0, 2.0 / 3.0, 1.0),  # batch_fraction
    )
    for idx, vals in enumerate(grid, 1):
        (
            explore_bias, explore_decay, success_satiation, depth_bias,
            evidence_weight, recovery_weight, risk_penalty,
            stop_threshold, batch_fraction,
        ) = vals
        yield {
            "policy_id": "dream_%05d" % idx,
            "explore_bias": explore_bias,
            "explore_decay": explore_decay,
            "success_satiation": success_satiation,
            "depth_bias": depth_bias,
            "quality_weight": 0.8,
            "evidence_weight": evidence_weight,
            "recovery_weight": recovery_weight,
            "risk_penalty": risk_penalty,
            "depth_penalty": 0.05,
            "stop_threshold": stop_threshold,
            "batch_fraction": batch_fraction,
        }


def improve_policy(world):
    evaluated = []
    for policy in candidate_policies():
        result = replay(world, policy)
        evaluated.append((result["reward"], policy["policy_id"], policy, result))
    evaluated.sort(key=lambda x: (-x[0], x[1]))
    selected = evaluated[0]
    incumbent_result = replay(world, INCUMBENT)
    return {
        "schema": "nexora-dream-replay-result/1.0",
        "world_id": world["world_id"],
        "scientific_status": "DIAGNOSTIC_ONLY" if world.get("scientific_status") == "DIAGNOSTIC_ONLY" else "ENGINEERING_ONLY",
        "candidate_count": len(evaluated),
        "incumbent": {"policy": INCUMBENT, "result": incumbent_result},
        "selected": {"policy": selected[2], "result": selected[3]},
        "replay_non_decrease": selected[3]["reward"] >= incumbent_result["reward"],
        "claim_ceiling": "Replay improvement on realized history only; no live/scientific improvement claim.",
    }


def adaptive_next_budget(live_history, replay_hint, floor_budget, ceiling_budget, fallback_budget, epsilon=1e-9):
    """Bounded between-cycle compute adaptation; never called inside a replay/live episode."""
    if len(live_history) < 2:
        return int(max(floor_budget, min(ceiling_budget, fallback_budget)))

    last = live_history[-1]
    prev = live_history[-2]
    current = int(last["attempt_budget"])
    delta = float(last["best_score"]) - float(prev["best_score"])

    if delta > epsilon:
        proposed = math.floor(current * 0.8)
    elif replay_hint.get("higher_exploration_improves") is True:
        proposed = math.ceil(current * 1.25)
    elif replay_hint.get("higher_exploration_wastes_work") is True:
        proposed = math.floor(current * 0.8)
    else:
        proposed = fallback_budget
    return int(max(floor_budget, min(ceiling_budget, proposed)))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default=DEFAULT_WORLD)
    ap.add_argument("--bootstrap-check", action="store_true")
    args = ap.parse_args(argv)

    world = load_world(args.world)
    result = improve_policy(world)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))

    if args.bootstrap_check:
        if world.get("scientific_status") != "DIAGNOSTIC_ONLY":
            print("BOOTSTRAP: FAIL — bootstrap world must be DIAGNOSTIC_ONLY", file=sys.stderr)
            return 1
        if not result["replay_non_decrease"]:
            print("BOOTSTRAP: FAIL — selected replay policy worse than incumbent", file=sys.stderr)
            return 1
        if result["candidate_count"] < 1000:
            print("BOOTSTRAP: FAIL — policy search unexpectedly small", file=sys.stderr)
            return 1
        print("BOOTSTRAP: PASS — prefix-only replay search completed", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

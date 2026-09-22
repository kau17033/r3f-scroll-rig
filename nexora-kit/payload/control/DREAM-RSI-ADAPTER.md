# NEXORA Dream-Replay Adapter v1.0

Status: **ENGINEERING ADAPTER / NOT SCIENTIFIC PROMOTION AUTHORITY**  
Effective: 2026-09-22  
Research basis: Dream-RSI, arXiv:2609.14858.

## 1. Purpose

Use completed NEXORA development/discovery histories as replay worlds for low-cost
**meta-exploration policy** improvement.

The adapter changes only how ORP/Controller allocates exploration:
- which branch/frontier to pursue;
- when to open a new branch;
- how much independent work to batch;
- when to stop;
- how to adjust the next-cycle exploration budget.

It MUST NOT change a frozen scientific evaluator, treatment, endpoint, estimator,
success rule, evidence requirement, authority rule, or experimental corpus.

## 2. Exact replay boundary

Replay is exact only over the **realized recorded support**.

A replay world may reveal an outcome only when that node was actually executed and recorded.
It MUST NOT:
- invent an unobserved child;
- estimate a hidden score with an LLM;
- treat semantic similarity as a recorded outcome;
- infer that a branch would have succeeded merely because a neighboring branch did;
- use future/unrevealed node scores in a policy decision.

Therefore "dreaming" here means off-policy navigation over recorded history, not a learned
world model and not a claim that unvisited counterfactuals are known.

## 3. Shared decision interface

A world is a rooted tree. The root may open multiple recorded branches in creation order.
Each non-root node has at most one recorded continuation. At each decision round the policy sees
only the revealed prefix and selects a legal batch of:
- the root, if another recorded root branch remains; and/or
- revealed leaves that have a recorded continuation.

Batch size is bounded by `max_parallelism`.

Actions marked `mandatory=true` are governance obligations known before execution. Replay may reorder them but may not optimize them away. Missing a mandatory action receives a fixed evaluator penalty and invalidates bootstrap selection.

## 4. Fixed evaluator / replay objective

Every replay world stores a fixed objective before policy comparison:

[
V = Q_{best} - lambda_c N - lambda_r R + lambda_p N / max(1,K)
]

where:
- `Q_best` = best recorded evaluator score revealed by the policy;
- `N` = revealed non-root attempts;
- `R` = cumulative recorded risk;
- `K` = completed replay decision rounds;
- missing mandatory governance actions incur a fixed penalty.

The objective is an **engineering controller objective**, not a scientific treatment effect.
Changing these weights creates a new controller-evaluation version.

## 5. Prefix-only policy

Policy priority may use only revealed:
- evaluator score;
- evidence gain;
- failure class / repairability;
- risk;
- depth;
- number of already opened roots;
- best score observed so far.

The policy may not inspect child outcomes before selecting the parent.

The current implementation searches a deterministic policy grid and always includes the incumbent.
Selecting the max replay objective therefore guarantees only:

[
V_{replay}(pi_{next}) ge V_{replay}(pi_{incumbent})
]

on the fixed replay pool. It does **not** imply live improvement.

## 6. Adaptive compute

Next-cycle exploration budget is allowed to change only between live cycles.

- sustained live improvement -> conserve compute within a configured floor;
- plateau + replay evidence that broader exploration improves attainment at acceptable cost -> expand;
- high exploration already tried without attainment improvement -> contract;
- insufficient/conflicting history -> conservative bootstrap budget.

The numeric 110→50 behavior reported by Dream-RSI is treated as empirical motivation, not copied as
a universal NEXORA constant.

## 7. Online/offline loop

```
ORP/Controller policy pi_t
        |
        v
prospective online discovery
        |
        v
immutable trace tree T_t + evaluator outcomes + cost/risk
        |
        v
replay-world validation
        |
        v
offline candidate policy search ("dreaming")
        |
        v
select pi_{t+1} on replay pool
        |
        v
prospective online redeployment
```

A replay result may update the **controller candidate**.
It may not close C3/C4/C5/C7 by itself.

## 8. C7 closure requirement

C7 remains open until the replay-selected controller is prospectively compared with a locked
controller baseline on new live worlds, with:
- evaluator unchanged;
- task/source distribution declared;
- predicted replay gain logged before execution;
- actual information/evidence gain logged after execution;
- actual cost/latency/risk logged;
- rollback possible;
- no unsupported scientific promotion;
- repeated/out-of-sample evidence sufficient for the predeclared decision rule.

## 9. Bootstrap world

`control/replay_worlds/bootstrap_convergence_20260922.json` is diagnostic-only.
It records realized engineering attempts from the convergence session to test replay mechanics.
Its scores are controller-engineering diagnostics and MUST NOT be used as evidence that Dream-RSI
improves NEXORA scientifically or economically.

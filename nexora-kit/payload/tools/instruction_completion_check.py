#!/usr/bin/env python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
FINAL20=["01_FINAL_CONVERGED_SPEC.md","02_REQUIREMENT_REGISTRY.md","03_CONTRADICTION_REGISTER.md","04_ARCHITECTURE.md","05_DEPENDENCY_GRAPH.md","06_CAPABILITY_MATRIX.md","07_REPOSITORY_GAP_ANALYSIS.md","08_SECURITY_MODEL.md","09_EVIDENCE_MODEL.md","10_STATE_MODEL.md","11_GATE_MODEL.md","12_AUTONOMY_AUTHORITY_MODEL.md","13_FAILURE_RECOVERY_MODEL.md","14_REPRODUCIBILITY_MODEL.md","15_COST_AND_SUSTAINABILITY_MODEL.md","16_IMPLEMENTATION_PLAN.md","17_VERIFICATION_PLAN.md","18_OPEN_QUESTIONS.md","19_DECISION_LOG.md","20_FINAL_AUDIT.md"]
REQ24=["MASTER_LOGIC_MAP.md","REQUIREMENT_MATRIX.md","DEPENDENCY_GRAPH.md","CONFLICT_REGISTER.md","GAP_REGISTER.md","FAILURE_MODE_REGISTER.md","EVIDENCE_GRAPH.md","PROTOCOL_REGISTER.md","ARTIFACT_SCHEMA.md","SKILL_REGISTRY.md","OSS_REGISTRY.md","TOOL_REGISTRY.md","COMMAND_REGISTRY.md","SECURITY_THREAT_MODEL.md","COST_MODEL.md","RESOURCE_MODEL.md","PERFORMANCE_MODEL.md","TEST_MATRIX.md","RECOVERY_MATRIX.md","AUTONOMOUS_LOOP_SPEC.md","SELF_REPAIR_SPEC.md","CAPABILITY_MATRIX.md","IMPLEMENTATION_ROADMAP.md","FINAL_ACCEPTANCE_CRITERIA.md"]
RESEARCH=['RESEARCH_STATE.md','RESEARCH_MANIFEST.json','RESEARCH_STATE.json','GATE_STATUS.json','EVIDENCE_LEDGER.jsonl']
missing=[]
for n in FINAL20:
    p=ROOT/'final'/n
    if not p.is_file(): missing.append(str(p.relative_to(ROOT)))
for n in REQ24:
    p=ROOT/'final'/'required'/n
    if not p.is_file(): missing.append(str(p.relative_to(ROOT)))
for n in RESEARCH:
    p=ROOT/'research'/n
    if not p.is_file(): missing.append(str(p.relative_to(ROOT)))
if not (ROOT/'final'/'00_INSTRUCTION_COMPLETION_MATRIX.md').is_file(): missing.append('final/00_INSTRUCTION_COMPLETION_MATRIX.md')
if missing:
    print('INSTRUCTION_COMPLETION: FAIL missing='+','.join(missing)); sys.exit(1)
m=json.loads((ROOT/'research'/'RESEARCH_MANIFEST.json').read_text())
if m.get('instruction_sha256')!='0a76facfbacf09ce4011e0f6b7d19846bbe5c967e51b986e9f1075439c4b8f02': print('INSTRUCTION_COMPLETION: FAIL instruction hash'); sys.exit(1)
a=(ROOT/'final'/'20_FINAL_AUDIT.md').read_text()
if 'INSTRUCTION_PROCESS: COMPLETE_TO_VALID_TERMINAL_STATES' not in a: print('INSTRUCTION_COMPLETION: FAIL audit'); sys.exit(1)
if 'SYSTEM/SCIENTIFIC COMPLETION: NOT YET TRUE' not in a: print('INSTRUCTION_COMPLETION: FAIL no-teleportation'); sys.exit(1)
print('INSTRUCTION_COMPLETION: PASS final20=%d required24=%d research=%d'%(len(FINAL20),len(REQ24),len(RESEARCH)))

# Agent Call Graph

**Generated**: 2026-08-15
**Agents**: 9 | **Edges**: 10

## Edge List

| Source | Target | Action |
|--------|--------|--------|
| human | devlead | Intake submission |
| devlead | intake | Decompose & triage |
| devlead | analyst | Root-cause analysis |
| devlead | fixer | Apply patch (L2, requires approval) |
| fixer | verifier | Run tests post-patch |
| verifier | devlead | Report results |
| devlead | release | Canary deploy (L3, requires approval) |
| release | knowledge | Capture runbook |
| devlead | orchestrator | Checkpoint / restore state |
| orchestrator | lifecycle | Persist lifecycle_state.json |

## Adjacency Summary

| Agent | Out-degree | In-degree | Role |
|-------|-----------|-----------|------|
| devlead | 5 | 2 | Manager |
| intake | 0 | 1 | Worker |
| analyst | 0 | 1 | Worker |
| fixer | 1 | 1 | Worker |
| verifier | 1 | 1 | Worker |
| release | 1 | 1 | Worker |
| knowledge | 0 | 1 | Worker |
| orchestrator | 1 | 1 | Worker |
| lifecycle | 0 | 1 | Worker |

## Cycle Check

No cycles detected — DAG confirmed (manager-mediated, no direct worker↔worker calls).

**Evidence ID**: E-L3-CALLGRAPH  |  **Tier**: L3 (Deductive)

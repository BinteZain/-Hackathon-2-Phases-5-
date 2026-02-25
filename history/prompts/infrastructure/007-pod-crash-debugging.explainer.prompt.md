---
id: 007
title: Kubernetes Pod Crash Debugging Guide
stage: explainer
date: 2026-02-21
surface: agent
model: qwen-coder
feature: phase3-troubleshooting
branch: main
user: MUHAMMAD AFNAN
command: Analyze why Kubernetes pods are crashing with causes, commands, and fixes
labels: ["kubernetes", "debugging", "troubleshooting", "pods", "crash", "phase3"]
links:
  spec: helm-charts/POD_CRASH_DEBUGGING.md
  ticket: null
  adr: null
  pr: null
files:
  - helm-charts/POD_CRASH_DEBUGGING.md
tests:
  - Command syntax validation
  - Exit code accuracy
---

## Prompt

Analyze why Kubernetes pods are crashing.

Provide:

- Possible causes
- Commands to inspect logs
- Commands to describe pods
- Resource debugging
- Network debugging
- Suggested fixes

## Response snapshot

Created comprehensive debugging guide (helm-charts/POD_CRASH_DEBUGGING.md) covering:

**Possible Causes (6 categories):**
1. Image Pull Issues (ImagePullBackOff, ErrImagePull)
2. Container Startup Failures (exit codes 1, 126, 127, 137, 143)
3. Configuration Issues (missing secrets/configmaps)
4. Resource Issues (OOMKilled, Evicted, Pending)
5. Probe Failures (liveness/readiness)
6. Network Issues (CNI, network policies)

**Log Inspection Commands:**
- Current logs, previous logs, follow mode
- Filter by time, search patterns
- All pods at once with prefix

**Pod Description:**
- Status section interpretation
- Events section (most important)
- Exit code meanings table

**Resource Debugging:**
- kubectl top pods/nodes
- OOMKilled detection
- Node capacity checks
- Resource quota validation

**Network Debugging:**
- Pod connectivity tests
- Service endpoint checks
- DNS resolution tests
- Network policy inspection

**Suggested Fixes (8 scenarios):**
1. Image pull issues
2. CrashLoopBackOff
3. OOMKilled (exit 137)
4. Probe failures
5. Missing ConfigMap/Secret
6. Pending pods
7. Network policy blocking
8. DNS issues

**Bonus:** PowerShell debugging script (debug-pods.ps1)

**Exit Code Reference:**
| Code | Meaning | Fix |
|------|---------|-----|
| 137 | OOMKilled | Increase memory |
| 126 | Not executable | Fix command |
| 127 | Not found | Fix command path |
| 143 | SIGTERM | Handle shutdown |

## Outcome

- ✅ Impact: Complete troubleshooting reference for pod crashes
- 🧪 Tests: Commands validated for kubectl v1.25+
- 📁 Files: 1 file created (helm-charts/POD_CRASH_DEBUGGING.md - 500+ lines)
- 🔁 Next prompts: Execute debugging commands on actual crashes
- 🧠 Reflection: Organized by symptom → diagnosis → fix workflow

## Evaluation notes (flywheel)

- Failure modes observed: None - documentation complete
- Graders run and results: N/A (documentation)
- Prompt variant: N/A
- Next experiment: Run debug-pods.ps1 on crashed pod

---
name: debug-rca
description: "Root Cause Analysis (RCA) & Full-Stack E2E Debugging Framework. Combines backend Node inspect debugging with Playwright browser automation to systematically isolate, reproduce, and verify frontend & API bugs."
user-invocable: true
keywords: [debug, root-cause, investigation, troubleshooting, sre, playwright, e2e, browser]
---

# Systematic Debugging & Full-Stack Root Cause Analysis (RCA)

A disciplined engineering framework to systematically investigate, reproduce, and verify bugs from the browser UI down to the backend database.

## Core Mandate: NO FIXES WITHOUT ROOT CAUSE PROOF

Do not jump straight into modifying code based on assumptions. Premature fixes introduce subtle regressions and fail edge cases. Every bug fix must follow the 4-phase RCA cycle.

```
+---------------------+     +----------------------+     +-----------------------+     +--------------------+
|  Phase 1: Symptom   | --> |  Phase 2: Evidence   | --> | Phase 3: Hypothesis   | --> |  Phase 4: Root Fix |
|   & Blast Radius    |     | Playwright + Inspect |     |  Isolate & Reproduce  |     |   & Verification   |
+---------------------+     +----------------------+     +-----------------------+     +--------------------+
```

---

## 4-Phase Full-Stack RCA Framework

### Phase 1: Symptom & Blast Radius
1. Identify the symptom: User reported UI freeze, button unresponsive, 500 API error, or failed Playwright test.
2. Determine blast radius: Which routes, components, or API endpoints are broken?

### Phase 2: Evidence Collection (Dual Trace: Browser + Backend)
1. **Check Services**: call `debug_status` first. It lists running app ports and Node inspectors and says which inspector serves which app port (e.g. "App on port 4201 -> debug_inspect_cdp inspectPort 9237"). Use the running services as they are. Only when nothing is running, call `debug_start_server` with a direct `node`/`tsx` command and `--inspect` on the API.
2. **Browser Trace (black box)**: call `debug_browser_run` on the page from the bug report, with `"headless": false` so the symptom is visible, then take a screenshot. Note what the page shows and which API requests it sent, with their status codes. A wrong result with HTTP 200 means the defect is in the backend logic, not in transport.
3. **Source Trace (grey box)**: read the backend code that serves that request, pick the line where the decision is made, then call `debug_inspect_cdp` once with:
   - `inspectPort` from step 1 (or omit it: the tool auto-detects when only one app inspector runs);
   - `breakpoints: [{ "file": "<module>/<file>.ts", "line": <line shown in the editor> }]` (source maps handle tsx/ts-node/bundlers; if `resolved` is false, read `reason` and `hint`);
   - `expressions`: the variables that decide the behaviour;
   - `trigger`: a command that sends the same request (e.g. `curl -s "<api url>"`), so one call reproduces the bug and returns the values read in RAM;
   - `pauseOnExceptions: "none"` for breakpoints only, `"all"` for HTTP 500s (framework-handled errors are caught exceptions).
   The result's `topFrame.sourceLine` is the source line where execution stopped: pausing on a line inside one branch proves that branch ran.
4. **Read-only rule**: evidence collection never edits application code and never restarts a server that is already running. If a tool cannot bind or attach, report what it returned.

### Phase 3: Hypothesis Formation & Isolation
1. Form 2-3 competing hypotheses (e.g. Frontend missing required payload field vs Backend validation schema rejected enum vs DB constraint violated).
2. Verify:
   - For backend test isolation: Run `debug_run_test`.
   - For test pollution: Run `skills/debug-rca/scripts/find-polluter.ps1` (or `.sh`).

### Phase 4: Report, then Fix on Request
1. Report: symptom (what the user sees), browser evidence (request + status), RAM evidence (variable values at `file:line`), root cause, and a proposed fix with the regression test that should cover it.
2. Edit code only when the user asks for the fix. Then fix at the root, re-run `debug_browser_run` with the same actions and the same `debug_inspect_cdp` call, and show that the values and the page are now correct.

---

## Toolset Overview

The plugin exposes the `debug-controller` MCP server:
- `debug_browser_run`: Full-stack browser scenario runner (Playwright) capturing console, network, and screenshots.
- `debug_inspect_cdp`: Attach to a running Node `--inspect` process, pause at a breakpoint or application exception, and read live variables from RAM.
- `debug_status`: Running app ports and Node inspectors (9229-9240), and which inspector serves which app.
- `debug_kill_ports`: Automatically resolve `EADDRINUSE` port collisions.
- `debug_start_server`: Launch application with `--inspect` enabled.
- `debug_stop_server`: Safely stop spawned debug server processes.
- `debug_run_test`: Run isolated unit/integration tests with clean stack trace capture.

---

## Reference Guides
Read detailed guides in `references/`:
- `references/frontend-e2e-debugging.md`: Full-stack browser & API correlation techniques.
- `references/systematic-debugging.md`: Detailed breakdown of hypothesis testing.
- `references/root-cause-tracing.md`: Backward call stack tracing technique.
- `references/log-and-ci-analysis.md`: Techniques for parsing server & CI logs.
- `references/verification.md`: Iron law of verification evidence.

---
name: overnight-sweep
description: "Autonomous Overnight Multi-Flow SRE Sweep with Parallel Workers, Standardized Test Design (BVA, Weak Robust EP), In-Memory CDP RAM Inspection, and Canvas Synthesis."
user-invocable: true
keywords: [overnight, sweep, parallel, testops, cdp, memory, canvas, batch, bva, equivalence-partitioning]
---

# Autonomous Overnight Multi-Flow SRE Sweep

A high-speed, parallelized overnight test orchestration protocol for web applications, integrating formal Software Testing methodologies.

## Execution Phases

### Phase 1: Environment Sanity (Zero Zombie Ports)
1. Query active listening ports: `debug_status({ ports: [3000, 4200, 4201, 8080, 9229, 9230] })`.
2. Terminate any orphaned or zombie processes: `debug_kill_ports({ ports: [9229, 9230] })`.
3. Launch the backend runtime with inspect enabled: `debug_start_server({ command: 'pnpm dev:api', inspectPort: 9229, app: 'api' })`.

### Phase 2: Parallel Partitioning (Fan-Out) with Standardized Test Matrix
Partition the test matrix into 3 concurrent worker pipelines, applying formal test design techniques:
- **Worker 1 (User & Catalog)**: `/login`, `/register`, `/products`, category taxonomy tree. (Áp dụng BVA $4n+1$ cho form validation và Decision Table cho quyền RBAC).
- **Worker 2 (Cart & Checkout)**: `/cart`, quantity mutations, delivery address, voucher calculations. (Áp dụng Weak Robust EP và Robustness BVA $6n+1$ cho số lượng & mã giảm giá).
- **Worker 3 (Financials & Escrow)**: `/payouts/estimate`, BigInt PPM taxes, `/disputes`. (Áp dụng Worst-case BVA $5^n$ và State Transition FSM cho chu trình thanh toán).

Dispatch each worker with an isolated `contextId` parameter in `debug_browser_run`:
- `contextId: 'worker-1'`
- `contextId: 'worker-2'`
- `contextId: 'worker-3'`

### Phase 3: In-Memory Exception Interception & White-Box Analysis
When any worker detects an HTTP 500:
1. Trigger `debug_inspect_cdp({ inspectPort: 9229, pauseOnExceptions: 'uncaught', expressions: ['sellerRank', 'order.isNegotiated'] })`.
2. Extract the exact callframe (`file:line`) and in-memory variable values directly from the heap.
3. Keep other workers running in parallel without stopping the suite.
4. Synthesize an isolated unit/integration regression test targeting Phủ cấp 1 (Statement Coverage) & Phủ cấp 2 (Branch Coverage) for the affected backend logic.

### Phase 4: Synthesis & Reporting (Fan-In)
Call `debug_export_overnight_report` to generate structured evidence alongside `screenshots/` (and optional `--record-video` recordings):
- `knowledge/OVERNIGHT-SWEEP-<date>.md` (Defect Dossier with SQA Metrics)
- `knowledge/OVERNIGHT-SWEEP-<date>.canvas.json` (Structured JSON graph for Obsidian Canvas or custom canvas tools, optionally synced via `CANVAS_RAG_DIR`)

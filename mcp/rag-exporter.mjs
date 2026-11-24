import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

/**
 * Evidence exporters.
 *
 * Integrity rule: these exporters only write what the caller passes in. They never invent
 * test cases, flows, latencies, source locations or heap values. Missing required evidence
 * is an error; missing optional evidence is written as "N/A".
 *
 * Outputs per report (in knowledge/):
 *   <base>.md           Markdown defect dossier (for people and for the agent to re-read later)
 *   <base>.canvas.json  Structured graph (sub_clusters schema) for custom canvas renderers
 *   <base>.canvas       JSON Canvas 1.0 file (https://jsoncanvas.org) that Obsidian Canvas opens directly
 */

const NA = 'N/A';

/**
 * Resolves an optional target directory for syncing exported canvas files (e.g. Obsidian vault or custom canvas workspace).
 * Priority: explicit args.canvasRagDir -> CANVAS_RAG_DIR env -> sibling workspace -> Desktop folder.
 */
function resolveCanvasRagDir(baseDir, args = {}) {
  const candidates = [
    args.canvasRagDir,
    process.env.CANVAS_RAG_DIR,
    path.resolve(baseDir, '..', '..', 'plugin-canvas-engineer', 'rag'),
    path.resolve(baseDir, '..', '..', 'canvas-note-engineer', 'rag'),
    path.join(os.homedir(), 'Desktop', 'plugin-canvas-engineer', 'rag')
  ].filter(Boolean);

  for (const dir of candidates) {
    if (fs.existsSync(dir)) return dir;
  }
  return null;
}

function syncCanvasArtifacts(baseDir, filenameBase, canvasPayload, jsonCanvas, args = {}) {
  if (args.syncToCanvasDir === false) {
    return { syncedToCanvas: false, canvasRagDir: null };
  }
  const targetDir = resolveCanvasRagDir(baseDir, args);
  if (!targetDir) {
    return { syncedToCanvas: false, canvasRagDir: null };
  }
  try {
    fs.writeFileSync(path.join(targetDir, filenameBase + '.canvas.json'), JSON.stringify(canvasPayload, null, 2), 'utf8');
    fs.writeFileSync(path.join(targetDir, filenameBase + '.canvas'), JSON.stringify(jsonCanvas, null, 2), 'utf8');
    return { syncedToCanvas: true, canvasRagDir: targetDir };
  } catch {
    return { syncedToCanvas: false, canvasRagDir: targetDir };
  }
}

const OBSIDIAN_COLORS = { rose: '1', amber: '3', emerald: '4', blue: '5', indigo: '6' };

function nodeToMarkdown(node) {
  const lines = ['### ' + node.title, '', node.summary || ''];
  const items = node.schematic_data?.items || [];
  if (node.schematic_data?.metric) lines.push('', '**' + node.schematic_data.metric + '**');
  if (items.length) lines.push('', ...items.map(i => '- ' + i.label));
  const dossier = node.incident_dossier;
  if (dossier) {
    lines.push('', '- Context: ' + dossier.boi_canh_tai, '- Root cause: ' + dossier.nguyen_nhan_goc_re, '- Blast radius: ' + dossier.ban_kinh_anh_huong);
  }
  return lines.join('\n');
}

/**
 * Converts the sub_clusters graph into a JSON Canvas 1.0 document: one group per sub-cluster laid out
 * as columns, one text node per graph node, edges chaining nodes inside a column and linking columns
 * (sequentially, or from the first column as a hub).
 */
function buildJsonCanvas(subClusters, { hub = false } = {}) {
  const COL_W = 420, NODE_W = 380, NODE_H = 260, GAP = 30, HEADER = 60;
  const nodes = [];
  const edges = [];
  const firstNodeIds = [];

  subClusters.forEach((cluster, col) => {
    const x = col * (COL_W + 60);
    const groupId = 'g' + col;
    const height = HEADER + cluster.nodes.length * (NODE_H + GAP);
    nodes.push({ id: groupId, type: 'group', label: cluster.name, x, y: 0, width: COL_W, height, color: OBSIDIAN_COLORS[cluster.theme] });

    cluster.nodes.forEach((node, row) => {
      const id = 'n' + col + '_' + row;
      nodes.push({
        id,
        type: 'text',
        text: nodeToMarkdown(node),
        x: x + (COL_W - NODE_W) / 2,
        y: HEADER + row * (NODE_H + GAP),
        width: NODE_W,
        height: NODE_H,
        color: node.badge_type === 'test_case_failed' || node.badge_type === 'root_cause_defect' ? '1'
          : node.badge_type === 'test_case_passed' || node.badge_type === 'regression_shield' ? '4' : undefined
      });
      if (row === 0) firstNodeIds.push(id);
      if (row > 0) edges.push({ id: 'e' + col + '_' + row, fromNode: 'n' + col + '_' + (row - 1), fromSide: 'bottom', toNode: id, toSide: 'top' });
    });
  });

  for (let i = 1; i < firstNodeIds.length; i++) {
    const from = hub ? firstNodeIds[0] : firstNodeIds[i - 1];
    edges.push({ id: 'c' + i, fromNode: from, fromSide: 'right', toNode: firstNodeIds[i], toSide: 'left' });
  }

  for (const n of nodes) if (n.color === undefined) delete n.color;
  return { nodes, edges };
}

function slugify(text) {
  return String(text)
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/đ/g, 'd')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 40);
}

function ensureKnowledgeDir(baseDir) {
  const knowledgeDir = path.resolve(baseDir, '..', 'knowledge');
  if (!fs.existsSync(knowledgeDir)) {
    fs.mkdirSync(knowledgeDir, { recursive: true });
  }
  return knowledgeDir;
}

/**
 * Exports a single test-suite / defect report:
 * 1. Markdown dossier (.md)
 * 2. Structured graph (.canvas.json) with 3 sub-clusters: Test Scenarios Matrix, Browser & Network Trace, RCA & Regression
 * 3. JSON Canvas (.canvas) for Obsidian
 */
export function exportRagReport(args, baseDir) {
  if (!args.title || !args.route) {
    throw new Error('debug_export_rag_report requires "title" and "route".');
  }
  if (!Array.isArray(args.testCases) || args.testCases.length === 0) {
    throw new Error('debug_export_rag_report requires a non-empty "testCases" array with the cases that were actually executed. The exporter does not generate sample results.');
  }

  const testId = args.testId || args.bugId || ('TS-' + Date.now().toString().slice(-6));
  const title = args.title;
  const route = args.route;
  const slug = slugify(title);
  const filenameBase = testId + '-' + slug;
  const knowledgeDir = ensureKnowledgeDir(baseDir);

  const testCases = args.testCases;
  const passedCount = testCases.filter(t => t.status === 'passed').length;
  const totalCount = testCases.length;
  const passRate = ((passedCount / totalCount) * 100).toFixed(1);
  const techniques = Array.isArray(args.testingTechniques) && args.testingTechniques.length > 0 ? args.testingTechniques : [NA];
  const src = args.sourceLocation || {};
  const srcText = src.file ? src.file + ':' + (src.line ?? '?') + ' (Function: ' + (src.function || NA) + ')' : NA;

  const mdSections = [
    '# [' + testId + '] ' + title,
    '',
    '- **Target Route**: `' + route + '`',
    '- **Execution Timestamp**: ' + new Date().toISOString(),
    '- **Test Result**: ' + passedCount + '/' + totalCount + ' Passed (' + passRate + '%) — ' + (passedCount === totalCount ? 'ALL GREEN' : 'DEFECT DETECTED'),
    '- **Severity**: ' + (args.severity || NA),
    '- **Testing Methodologies**: ' + techniques.join(', '),
    '',
    '---',
    '',
    '## 1. Test Scenarios Matrix',
    ...testCases.map(tc => '- **' + (tc.id || 'TC') + '**: ' + tc.title + ' -> **' + (tc.status === 'passed' ? 'PASSED' : 'FAILED') + '** (' + (tc.metric || NA) + (tc.technique ? ' | Technique: ' + tc.technique : '') + ')\n  *Summary*: ' + (tc.summary || NA)),
    '',
    '---',
    '',
    '## 2. Browser & Network Execution Trace (Playwright)',
    '- **DOM Interaction**: ' + (args.actionDescription ? '`' + args.actionDescription + '`' : NA),
    '- **Console Errors**:',
    '```text',
    args.symptoms?.consoleError || 'None recorded.',
    '```',
    '- **Failed HTTP Request**:',
    '```text',
    args.symptoms?.failedRequest || 'None recorded.',
    '```',
    '- **Screenshot Artifact**: ' + (args.symptoms?.screenshotPath ? '`' + args.symptoms.screenshotPath + '`' : NA),
    '',
    '---',
    '',
    '## 3. Root Cause Analysis (RCA) & Regression Defense',
    '- **Source Location**: ' + (src.file ? '`' + srcText + '`' : NA),
    '- **Root Cause**:',
    args.rootCause || NA,
    '- **Automated Regression Suite**: ' + (args.regressionTestFile ? '`' + args.regressionTestFile + '`' : NA)
  ];

  if (args.cdpHeapInspection) {
    mdSections.push('', '### CDP In-Memory Heap Snapshot', '```json', JSON.stringify(args.cdpHeapInspection, null, 2), '```');
  }
  if (args.coverageMetrics) {
    mdSections.push('', '### White-Box Coverage & Complexity Metrics', '```json', JSON.stringify(args.coverageMetrics, null, 2), '```');
  }

  const mdPath = path.join(knowledgeDir, filenameBase + '.md');
  fs.writeFileSync(mdPath, mdSections.join('\n'), 'utf8');

  const rcaNodes = [
    {
      title: 'Root Cause: ' + (src.file ? path.basename(src.file) + (src.line ? ' (Line ' + src.line + ')' : '') : NA),
      role: 'root_cause',
      badge_type: 'root_cause_defect',
      summary: (src.function ? 'Function ' + src.function + ': ' : '') + (args.rootCause || NA),
      schematic_template: 'table_row_lock',
      incident_dossier: {
        boi_canh_tai: (args.actionDescription || NA) + ' at ' + route,
        nguyen_nhan_goc_re: args.rootCause || NA,
        ban_kinh_anh_huong: args.blastRadius || NA,
        chien_luoc_phong_thu: args.mitigation || NA
      },
      incident_cases: [
        {
          id: 'defect_' + testId.toLowerCase().replace(/[^a-z0-9]/g, '_'),
          title,
          traffic_profile: 'E2E Playwright simulation',
          root_cause_analysis: args.rootCause || NA,
          blast_radius: args.blastRadius || NA,
          cascading_failure_path: [
            '1. [User Action]: ' + (args.actionDescription || NA),
            '2. [HTTP Fail]: ' + (args.symptoms?.failedRequest || NA),
            '3. [Frontend Error]: ' + (args.symptoms?.consoleError || NA),
            '4. [Backend Fault]: ' + srcText
          ],
          mitigation_strategy: args.mitigation || NA
        }
      ]
    },
    {
      title: 'Regression Defense Suite',
      role: 'defense_test',
      badge_type: args.regressionTestFile ? 'regression_shield' : undefined,
      summary: args.regressionTestFile ? 'Regression test: ' + args.regressionTestFile : 'No regression test recorded.',
      schematic_template: 'default',
      schematic_data: {
        items: [
          { label: 'Test File: ' + (args.regressionTestFile ? path.basename(args.regressionTestFile) : NA), status: args.regressionTestFile ? 'ok' : 'warn' }
        ]
      }
    }
  ];

  const subClusters = [
    {
      sub_cluster_id: 'sub_test_scenarios',
      name: '📋 Test Scenarios Matrix',
      theme: 'indigo',
      nodes: testCases.map(tc => ({
        title: (tc.id || 'TC') + ': ' + tc.title,
        role: 'test_case',
        badge_type: tc.status === 'passed' ? 'test_case_passed' : 'test_case_failed',
        summary: tc.summary || NA,
        schematic_template: 'pipeline_filter',
        schematic_data: {
          status: tc.status,
          metric: tc.metric || NA,
          items: [
            { label: 'Verdict: ' + String(tc.status).toUpperCase(), status: tc.status === 'passed' ? 'ok' : 'error' },
            ...(tc.technique ? [{ label: 'Technique: ' + tc.technique, status: 'info' }] : [])
          ]
        }
      }))
    },
    {
      sub_cluster_id: 'sub_browser_trace',
      name: '🎭 Browser & Network Trace (Playwright)',
      theme: 'blue',
      nodes: [
        {
          title: 'Playwright: DOM Interaction (' + route + ')',
          role: 'browser_action',
          badge_type: 'playwright_trace',
          summary: args.actionDescription || NA,
          schematic_template: 'default',
          schematic_data: {
            items: [
              { label: 'Route: ' + route, status: 'info' },
              { label: 'Console Error: ' + (args.symptoms?.consoleError || 'None'), status: args.symptoms?.consoleError ? 'error' : 'ok' },
              { label: 'Artifact: ' + (args.symptoms?.screenshotPath ? path.basename(args.symptoms.screenshotPath) : NA), status: 'info' }
            ]
          }
        },
        {
          title: 'API Intercept',
          role: 'gateway',
          summary: 'Intercepted backend HTTP response: ' + (args.symptoms?.failedRequest || 'no failed request recorded'),
          schematic_template: 'circuit_breaker_backoff',
          schematic_data: {
            metric: args.symptoms?.failedRequest || 'No failed request',
            items: [
              { label: args.symptoms?.failedRequest ? 'Failed Request: ' + args.symptoms.failedRequest : 'No failed request recorded', status: args.symptoms?.failedRequest ? 'error' : 'ok' },
              { label: 'Endpoint: ' + route, status: 'info' }
            ]
          }
        }
      ]
    },
    {
      sub_cluster_id: 'sub_defect_defense',
      name: '🔍 Root Cause Analysis & Regression Defense',
      theme: 'rose',
      nodes: rcaNodes
    }
  ];

  const canvasPayload = {
    domain_id: 'testops_' + slug.replace(/-/g, '_'),
    cluster_name: '[TEST SUITE] ' + testId + ': ' + title,
    cluster_theme: passedCount === totalCount ? 'emerald' : 'rose',
    sub_title: 'Pass Rate: ' + passRate + '% (' + passedCount + '/' + totalCount + ' Passed)',
    is_public_interface: true,
    nodes: [],
    sub_clusters: subClusters
  };

  const jsonPath = path.join(knowledgeDir, filenameBase + '.canvas.json');
  fs.writeFileSync(jsonPath, JSON.stringify(canvasPayload, null, 2), 'utf8');

  const jsonCanvas = buildJsonCanvas(subClusters);
  const obsidianCanvasPath = path.join(knowledgeDir, filenameBase + '.canvas');
  fs.writeFileSync(obsidianCanvasPath, JSON.stringify(jsonCanvas, null, 2), 'utf8');

  const { syncedToCanvas, canvasRagDir } = syncCanvasArtifacts(baseDir, filenameBase, canvasPayload, jsonCanvas, args);

  return {
    testId,
    title,
    passRate: passRate + '%',
    mdPath,
    jsonPath,
    obsidianCanvasPath,
    syncedToCanvas,
    canvasRagDir,
    canvasSubClustersCount: subClusters.length
  };
}

/**
 * Exports a consolidated multi-flow sweep report:
 * 1. Markdown report (OVERNIGHT-SWEEP-<date>.md) with flow breakdown & RCA
 * 2. Structured graph (.canvas.json) and JSON Canvas (.canvas) for Obsidian
 */
export function exportOvernightSweepReport(args = {}, baseDir = import.meta.dirname) {
  if (!Array.isArray(args.flows) || args.flows.length === 0) {
    throw new Error('debug_export_overnight_report requires a non-empty "flows" array with the results that were actually collected. The exporter does not generate sample flows.');
  }

  const dateStr = args.date || new Date().toISOString().slice(0, 10);
  const sweepId = args.sweepId || ('SWEEP-' + dateStr.replace(/-/g, ''));
  const knowledgeDir = ensureKnowledgeDir(baseDir);
  const flows = args.flows;

  const totalFlows = flows.length;
  const passedFlows = flows.filter(f => f.status === 'passed').length;
  const failedFlows = totalFlows - passedFlows;
  const overallPassRate = ((passedFlows / totalFlows) * 100).toFixed(1);
  const totalCases = flows.reduce((acc, f) => acc + (f.totalCases || 0), 0);
  const passedCases = flows.reduce((acc, f) => acc + (f.passedCases || 0), 0);
  const casesRate = totalCases > 0 ? ((passedCases / totalCases) * 100).toFixed(1) + '%' : NA;
  const anyHeap = flows.some(f => f.defect?.cdpHeapInspection && Object.keys(f.defect.cdpHeapInspection).length > 0);
  const fmtLatency = (f) => (typeof f.avgLatencyMs === 'number' ? f.avgLatencyMs + 'ms' : NA);

  const filenameBase = 'OVERNIGHT-SWEEP-' + dateStr;
  const mdPath = path.join(knowledgeDir, filenameBase + '.md');
  const jsonPath = path.join(knowledgeDir, filenameBase + '.canvas.json');

  const mdLines = [
    '# 🌙 Multi-Flow Sweep Report: ' + dateStr,
    '',
    '- **Sweep ID**: `' + sweepId + '`',
    '- **Execution Timestamp**: `' + new Date().toISOString() + '`',
    '- **Total Flows Tested**: ' + totalFlows,
    '- **Flow Status**: **' + passedFlows + '/' + totalFlows + ' Passed (' + overallPassRate + '%)** — ' + (failedFlows === 0 ? '✅ ALL GREEN' : ('❌ ' + failedFlows + ' FLOW DEFECTS DETECTED')),
    '- **Total Test Cases Executed**: ' + passedCases + '/' + totalCases + ' Passed (' + casesRate + ')',
    '- **CDP heap evidence attached**: ' + (anyHeap ? 'yes' : 'no'),
    '',
    '---',
    '',
    '## 📊 1. Multi-Flow Health Summary Matrix',
    '',
    '| Flow ID | Business Flow | Route | Status | Test Cases | Avg Latency | Notes |',
    '|---|---|---|---|---|---|---|',
    ...flows.map(f => '| **' + f.flowId + '** | ' + (f.name || NA) + ' | `' + (f.route || NA) + '` | ' + (f.status === 'passed' ? 'PASSED ✅' : 'FAILED ❌') + ' | ' + (f.passedCases ?? NA) + '/' + (f.totalCases ?? NA) + ' | ' + fmtLatency(f) + ' | ' + (f.summary || '') + ' |'),
    '',
    '---',
    '',
    '## 🔍 2. Defect Dossier (Root Cause & CDP Heap Evidence)',
    ''
  ];

  const failedFlowList = flows.filter(f => f.status === 'failed');
  if (failedFlowList.length === 0) {
    mdLines.push('> ✅ No failed flows in this sweep.');
  } else {
    failedFlowList.forEach((f, idx) => {
      const d = f.defect || {};
      mdLines.push(
        '### ' + (idx + 1) + '. [' + f.flowId + '] ' + (f.name || NA),
        '- **Target Route**: `' + (f.route || NA) + '`',
        '- **HTTP Network Intercept**: ' + (d.failedRequest || d.httpStatus || NA),
        '- **Frontend Console Error**: ' + (d.consoleError || NA),
        '- **Source Code Location**: ' + (d.sourceLocation?.file ? '`' + d.sourceLocation.file + ':' + (d.sourceLocation.line ?? '?') + '` (Function: `' + (d.sourceLocation.function || NA) + '`)' : NA),
        '',
        '#### 🔬 CDP Heap Variables:',
        d.cdpHeapInspection ? '```json\n' + JSON.stringify(d.cdpHeapInspection, null, 2) + '\n```' : NA,
        '',
        '#### 💡 Root Cause Analysis (RCA):',
        d.rootCause || NA,
        '',
        '- **Regression Test**: ' + (d.regressionTest ? '`' + d.regressionTest + '`' : NA),
        '',
        '---'
      );
    });
  }

  fs.writeFileSync(mdPath, mdLines.join('\n'), 'utf8');

  const canvasSubClusters = [
    {
      sub_cluster_id: 'sub_executive_summary',
      name: '📊 Sweep Overview & KPIs',
      theme: failedFlows === 0 ? 'emerald' : 'amber',
      nodes: [
        {
          title: 'Sweep: ' + dateStr,
          role: 'gateway',
          badge_type: failedFlows === 0 ? 'test_case_passed' : 'test_case_failed',
          summary: totalFlows + ' business flows. Pass rate: ' + overallPassRate + '%. ' + failedFlows + ' failed flow(s).',
          schematic_template: 'circuit_breaker_backoff',
          schematic_data: {
            metric: 'Pass Rate: ' + overallPassRate + '%',
            items: [
              { label: 'Flows: ' + passedFlows + '/' + totalFlows + ' Passed', status: failedFlows === 0 ? 'ok' : 'warn' },
              { label: 'Test Cases: ' + passedCases + '/' + totalCases, status: 'info' },
              { label: 'CDP heap evidence: ' + (anyHeap ? 'attached' : 'none'), status: anyHeap ? 'ok' : 'info' }
            ]
          }
        }
      ]
    }
  ];

  flows.forEach(flow => {
    const subClusterId = 'sub_' + String(flow.flowId).toLowerCase().replace(/[^a-z0-9]/g, '_');

    if (flow.status === 'passed') {
      canvasSubClusters.push({
        sub_cluster_id: subClusterId,
        name: '✅ [' + flow.flowId + '] ' + (flow.name || NA),
        theme: 'emerald',
        nodes: [
          {
            title: flow.flowId + ': ' + (flow.name || NA),
            role: 'test_case',
            badge_type: 'test_case_passed',
            summary: flow.summary || NA,
            schematic_template: 'pipeline_filter',
            schematic_data: {
              metric: 'Avg Latency: ' + fmtLatency(flow),
              items: [
                { label: 'Test Cases: ' + (flow.passedCases ?? NA) + '/' + (flow.totalCases ?? NA) + ' Passed', status: 'ok' },
                { label: 'Route: ' + (flow.route || NA), status: 'info' }
              ]
            }
          }
        ]
      });
      return;
    }

    const d = flow.defect || {};
    const nodes = [
      {
        title: 'Playwright Trace: ' + (flow.name || flow.flowId),
        role: 'browser_action',
        badge_type: 'playwright_trace',
        summary: 'Failure observed at ' + (flow.route || NA) + ': ' + (d.failedRequest || d.httpStatus || flow.summary || NA),
        schematic_template: 'default',
        schematic_data: {
          items: [
            { label: 'Route: ' + (flow.route || NA), status: 'info' },
            { label: 'Error: ' + (d.consoleError || NA), status: d.consoleError ? 'error' : 'info' },
            { label: 'Request: ' + (d.failedRequest || NA), status: d.failedRequest ? 'error' : 'info' }
          ]
        }
      }
    ];
    if (d.cdpHeapInspection) {
      nodes.push({
        title: 'CDP Heap: ' + (d.sourceLocation?.function || flow.flowId),
        role: 'gateway',
        summary: 'Variables evaluated on the paused call frame via CDP: ' + JSON.stringify(d.cdpHeapInspection),
        schematic_template: 'table_row_lock',
        schematic_data: {
          metric: 'Captured via CDP',
          items: Object.entries(d.cdpHeapInspection).map(([k, v]) => ({
            label: k + ': ' + (typeof v === 'object' ? JSON.stringify(v) : v),
            status: v === null || v === 'NaN' ? 'error' : 'warn'
          }))
        }
      });
    }
    nodes.push({
      title: 'Root Cause: ' + (d.sourceLocation?.file ? path.basename(d.sourceLocation.file) + ':' + (d.sourceLocation.line ?? '?') : NA),
      role: 'root_cause',
      badge_type: 'root_cause_defect',
      summary: d.rootCause || NA,
      schematic_template: 'table_row_lock',
      incident_dossier: {
        boi_canh_tai: 'Flow ' + flow.flowId + ' at ' + (flow.route || NA),
        nguyen_nhan_goc_re: d.rootCause || NA,
        ban_kinh_anh_huong: 'Business Flow ' + (flow.name || flow.flowId),
        chien_luoc_phong_thu: d.mitigation || NA
      }
    });
    if (d.regressionTest) {
      nodes.push({
        title: 'Regression Test: ' + path.basename(d.regressionTest),
        role: 'defense_test',
        badge_type: 'regression_shield',
        summary: 'Regression test ' + d.regressionTest,
        schematic_template: 'default',
        schematic_data: { items: [{ label: 'Test File: ' + path.basename(d.regressionTest), status: 'ok' }] }
      });
    }

    canvasSubClusters.push({
      sub_cluster_id: subClusterId,
      name: '❌ [' + flow.flowId + '] ' + (flow.name || NA),
      theme: 'rose',
      nodes
    });
  });

  const canvasPayload = {
    domain_id: 'sweep_' + sweepId.toLowerCase().replace(/[^a-z0-9]/g, '_'),
    cluster_name: '[SWEEP] ' + dateStr + ': ' + passedFlows + '/' + totalFlows + ' Flows Passed (' + overallPassRate + '%)',
    cluster_theme: failedFlows === 0 ? 'emerald' : 'rose',
    sub_title: totalFlows + ' flows | ' + failedFlows + ' failed',
    is_public_interface: true,
    nodes: [],
    sub_clusters: canvasSubClusters
  };

  fs.writeFileSync(jsonPath, JSON.stringify(canvasPayload, null, 2), 'utf8');

  const jsonCanvas = buildJsonCanvas(canvasSubClusters, { hub: true });
  const obsidianCanvasPath = path.join(knowledgeDir, filenameBase + '.canvas');
  fs.writeFileSync(obsidianCanvasPath, JSON.stringify(jsonCanvas, null, 2), 'utf8');

  const { syncedToCanvas, canvasRagDir } = syncCanvasArtifacts(baseDir, filenameBase, canvasPayload, jsonCanvas, args);

  return {
    sweepId,
    dateStr,
    totalFlows,
    passedFlows,
    failedFlows,
    overallPassRate: overallPassRate + '%',
    mdPath,
    jsonPath,
    obsidianCanvasPath,
    syncedToCanvas,
    canvasRagDir,
    subClustersCount: canvasPayload.sub_clusters.length
  };
}

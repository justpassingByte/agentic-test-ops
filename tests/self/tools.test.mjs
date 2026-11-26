/**
 * Self-tests for the Agentic TestOps MCP tools. Every tool call goes through the real MCP stdio
 * protocol (scripts/mcp-call.mjs -> mcp/server.mjs). Needs no external system, so it runs in CI.
 *
 *   node --test --test-concurrency=1 tests/self/tools.test.mjs
 */
import { test, after } from 'node:test';
import assert from 'node:assert/strict';
import { spawn, execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '..', '..');
const CLI = path.join(ROOT, 'scripts', 'mcp-call.mjs');
const WORK = fs.mkdtempSync(path.join(os.tmpdir(), 'testops-self-'));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const procs = [];

function mcp(tool, args = {}) {
  const file = path.join(WORK, `args-${Date.now()}-${Math.random().toString(36).slice(2)}.json`);
  fs.writeFileSync(file, JSON.stringify(args));
  let out;
  try {
    out = execFileSync(process.execPath, [CLI, tool, `@${file}`], { cwd: ROOT, encoding: 'utf8', maxBuffer: 20 * 1024 * 1024 });
  } catch (err) {
    out = err.stdout || '';   // tool returned isError=true: the message itself is the result under test
  }
  try { return JSON.parse(out); } catch { return out; }
}
function mcpAsync(tool, args = {}) {
  const file = path.join(WORK, `args-${Date.now()}-${Math.random().toString(36).slice(2)}.json`);
  fs.writeFileSync(file, JSON.stringify(args));
  return new Promise((resolve) => {
    const p = spawn(process.execPath, [CLI, tool, `@${file}`], { cwd: ROOT });
    let out = '';
    p.stdout.on('data', (d) => (out += d));
    p.on('exit', () => { try { resolve(JSON.parse(out)); } catch { resolve(out); } });
  });
}
function start(cmd, args, opts = {}) {
  // detached on POSIX -> own process group, so after() can kill wrapper + children (npm -> sh -> node) together.
  const p = spawn(cmd, args, { cwd: WORK, stdio: ['ignore', 'pipe', 'pipe'], detached: process.platform !== 'win32', ...opts });
  let log = '';
  p.stdout.on('data', (d) => (log += d));
  p.stderr.on('data', (d) => (log += d));
  procs.push(p);
  return { proc: p, log: () => log };
}
after(() => {
  for (const p of procs) {
    try {
      if (process.platform === 'win32') execFileSync('taskkill', ['/F', '/T', '/PID', String(p.pid)], { stdio: 'ignore' });
      else process.kill(-p.pid, 'SIGKILL');   // whole process group
    } catch {}
    p.stdout?.destroy();
    p.stderr?.destroy();
  }
  fs.rmSync(WORK, { recursive: true, force: true });
});

// A tiny SUT: framework-style handler that catches the error and answers 500, plus a library that throws/catches internally.
fs.mkdirSync(path.join(WORK, 'node_modules', 'noisylib'), { recursive: true });
fs.writeFileSync(path.join(WORK, 'node_modules', 'noisylib', 'package.json'), '{"name":"noisylib","type":"module","main":"index.mjs"}');
fs.writeFileSync(path.join(WORK, 'node_modules', 'noisylib', 'index.mjs'), 'export function parse(s){ try { return JSON.parse(s); } catch { return null; } }\n');
fs.writeFileSync(path.join(WORK, 'sut.mjs'), `
import http from 'node:http';
import { parse } from 'noisylib';
const port = Number(process.env.PORT);
http.createServer((req, res) => {
  if (req.url === '/page') { res.setHeader('content-type', 'text/html'); return res.end('<script>console.error("boom"); fetch("/api")</script>'); }
  parse('{bad');
  try {
    const order = { isNegotiated: true, sellerRank: null };
    const allowed = ['paid'];
    if (!allowed.includes(order.isNegotiated ? 'unpaid' : 'paid')) { /* decision point */ }
    res.end(String(order.sellerRank.discount));
  } catch { res.statusCode = 500; res.end('500'); }
}).listen(port, '127.0.0.1');
`);
fs.writeFileSync(path.join(WORK, 'package.json'), '{"name":"sut","private":true,"scripts":{"dev":"node sut.mjs"}}');

test('MCP handshake exposes the 9 tools', () => {
  const out = execFileSync(process.execPath, [CLI, '--list'], { cwd: ROOT, encoding: 'utf8' });
  assert.match(out, /debug-controller .*: 9 tools/);
  for (const t of ['debug_inspect_cdp', 'debug_browser_run', 'debug_run_test', 'debug_export_rag_report', 'debug_export_overnight_report', 'debug_status', 'debug_kill_ports', 'debug_start_server', 'debug_stop_server']) {
    assert.match(out, new RegExp(`- ${t}\\b`));
  }
});

test('debug_inspect_cdp pauses on a framework-handled 500, skips library exceptions, evaluates heap values', async () => {
  start(process.execPath, ['--inspect=127.0.0.1:9461', 'sut.mjs'], { env: { ...process.env, PORT: '4961' } });
  await sleep(1500);
  const pending = mcpAsync('debug_inspect_cdp', { inspectPort: 9461, timeoutMs: 8000, expressions: ['order.isNegotiated', 'order.sellerRank'] });
  await sleep(1500);
  const status = await fetch('http://127.0.0.1:4961/').then((r) => r.status);
  const r = await pending;
  assert.equal(status, 500);
  assert.equal(r.status, 'PAUSED');
  assert.match(r.topFrame.url, /sut\.mjs$/);
  assert.ok(r.skippedLibraryExceptions >= 1);
  assert.equal(r.evaluatedVariables['order.isNegotiated'].value, true);
  assert.equal(r.evaluatedVariables['order.sellerRank'].value, null);
});

test('debug_inspect_cdp source-text breakpoint works without line numbers', async () => {
  const pending = mcpAsync('debug_inspect_cdp', { inspectPort: 9461, timeoutMs: 8000, pauseOnExceptions: 'none',
    breakpoints: [{ file: 'sut.mjs', match: 'allowed.includes(' }], expressions: ['allowed', 'order.isNegotiated'] });
  await sleep(1500);
  await fetch('http://127.0.0.1:4961/');
  const r = await pending;
  assert.equal(r.status, 'PAUSED');
  assert.equal(r.breakpointsResolved[0].resolved, true);
  assert.deepEqual(r.evaluatedVariables.allowed.value, ['paid']);
});

test('debug_status finds the Node inspector and links it to the app port it serves', () => {
  const r = mcp('debug_status', { ports: [4961, 9461] });
  const insp = r.inspectors.find(i => i.inspectPort === 9461);
  assert.ok(insp, 'inspector 9461 not detected');
  assert.deepEqual(insp.servesAppPorts, [4961]);
  assert.equal(insp.packageManager, false);
  assert.ok(r.hints.some(h => /4961 .*inspectPort 9461/.test(h)), JSON.stringify(r.hints));
});

test('debug_inspect_cdp source-text breakpoint without "file" searches every application script', async () => {
  const pending = mcpAsync('debug_inspect_cdp', { inspectPort: 9461, timeoutMs: 8000, pauseOnExceptions: 'none',
    breakpoints: [{ match: 'allowed.includes(' }], expressions: ['allowed'] });
  await sleep(1500);
  await fetch('http://127.0.0.1:4961/');
  const r = await pending;
  assert.equal(r.status, 'PAUSED');
  assert.equal(r.breakpointsResolved[0].resolved, true);
  assert.match(r.breakpointsResolved[0].url, /sut\.mjs$/);
  assert.deepEqual(r.evaluatedVariables.allowed.value, ['paid']);
});

// Transpiled-code SUT (what tsx produces): the original 7-line file is squeezed onto 2 generated lines,
// with an inline source map. A breakpoint on ORIGINAL line 5 must bind through the map.
function vlq(n) {
  const B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  let v = n < 0 ? (-n << 1) | 1 : n << 1, out = '';
  do { let d = v & 31; v >>>= 5; if (v) d |= 32; out += B64[d]; } while (v);
  return out;
}
{
  const gen0 = `import http from 'node:http'; const port = Number(process.env.PORT);`;
  const parts = [`http.createServer((req, res) => { `, `const price = 42; `, `const label = 'x' + price; `, `res.end(label); `, `}).listen(port, '127.0.0.1');`];
  // generated line 1: each part maps to original lines 3..7 (0-based 2..6), column 0
  let col = 0, prevCol = 0, prevSrcLine = 0;
  const segs = parts.map((p, i) => { const s = vlq(col - prevCol) + vlq(0) + vlq((2 + i) - prevSrcLine) + vlq(0); prevCol = col; prevSrcLine = 2 + i; col += p.length; return s; });
  const map = { version: 3, sources: ['sm.mjs'], names: [], mappings: `${vlq(0)}${vlq(0)}${vlq(0)}${vlq(0)};${segs.join(',')}` };
  // line-0 segment maps to original line 0; line-1 deltas are relative to it (srcLine 0 -> 2 ...).
  fs.writeFileSync(path.join(WORK, 'sm.mjs'), `${gen0}\n${parts.join('')}\n//# sourceMappingURL=data:application/json;base64,${Buffer.from(JSON.stringify(map)).toString('base64')}\n`);
}

test('debug_inspect_cdp {file, line} uses the ORIGINAL line through the source map (tsx-style code)', async () => {
  start(process.execPath, ['--inspect=127.0.0.1:9463', 'sm.mjs'], { env: { ...process.env, PORT: '4963' } });
  await sleep(1500);
  const r = mcp('debug_inspect_cdp', { inspectPort: 9463, timeoutMs: 15000, pauseOnExceptions: 'none',
    breakpoints: [{ file: 'sm.mjs', line: 5 }], expressions: ['price'],
    trigger: { command: `node -e "fetch('http://127.0.0.1:4963/').then(r => r.text()).then(t => console.log('BODY ' + t))"` } });
  assert.equal(r.status, 'PAUSED');
  assert.equal(r.breakpointsResolved[0].resolved, true);
  assert.equal(r.breakpointsResolved[0].via, 'source map');
  assert.equal(r.breakpointsResolved[0].generatedLine, 2);
  assert.equal(r.topFrame.sourceLine, 5);
  assert.equal(r.evaluatedVariables.price.value, 42);
  assert.match(r.trigger.output, /BODY x42/);
});

test('debug_inspect_cdp trigger: attaches first, runs the reproduction command, returns its output and the RAM values', () => {
  const r = mcp('debug_inspect_cdp', { inspectPort: 9461, timeoutMs: 15000, pauseOnExceptions: 'none',
    breakpoints: [{ file: 'sut.mjs', match: 'allowed.includes(' }], expressions: ['allowed', 'order.isNegotiated'],
    trigger: { command: `node -e "fetch('http://127.0.0.1:4961/').then(r => console.log('HTTP ' + r.status))"` } });
  assert.equal(r.status, 'PAUSED');
  assert.deepEqual(r.evaluatedVariables.allowed.value, ['paid']);
  assert.equal(r.trigger.exitCode, 0);
  assert.match(r.trigger.output, /HTTP 500/);
});

test('debug_inspect_cdp trigger that never reaches the breakpoint ends early as CLEAN', () => {
  const t0 = Date.now();
  const r = mcp('debug_inspect_cdp', { inspectPort: 9461, timeoutMs: 15000, pauseOnExceptions: 'none',
    breakpoints: [{ file: 'sut.mjs', match: 'allowed.includes(' }], trigger: { command: 'node -e "process.exit(3)"' } });
  assert.equal(r.status, 'CLEAN_NO_EXCEPTION');
  assert.equal(r.trigger.exitCode, 3);
  assert.ok(Date.now() - t0 < 10000, 'did not end early');
});

test('debug_inspect_cdp refuses a package-manager process holding the inspect port', async () => {
  const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';
  start(npm, ['run', 'dev'], { shell: process.platform === 'win32', env: { ...process.env, PORT: '4962', NODE_OPTIONS: '--inspect=127.0.0.1:9462' } });
  await sleep(4000);
  const r = mcp('debug_inspect_cdp', { inspectPort: 9462, timeoutMs: 2000 });
  assert.match(typeof r === 'string' ? r : JSON.stringify(r), /package-manager/);
});

test('debug_browser_run reports HTTP failures and console errors with a screenshot', () => {
  const r = mcp('debug_browser_run', { url: 'http://127.0.0.1:4961/page', actions: [{ type: 'wait', ms: 1500 }], timeoutMs: 30000 });
  assert.equal(r.status, 'FAILED');
  assert.ok(r.failedRequests.some((f) => f.status === 500), 'HTTP 500 not captured');
  assert.ok(r.consoleErrors.some((c) => /boom/.test(c.text)), 'console.error not captured');
  assert.ok(r.apiRequests.some((q) => q.url.endsWith('/api') && q.status === 500), 'fetch request not listed in apiRequests');
  assert.ok(r.screenshotPath && path.isAbsolute(r.screenshotPath));
  fs.rmSync(path.resolve(r.screenshotPath), { force: true });
});

test('exporters refuse missing evidence and write a valid JSON Canvas', () => {
  const refused = mcp('debug_export_rag_report', { title: 'x', route: '/x', syncToCanvasDir: false });
  assert.match(String(refused), /testCases/);
  const r = mcp('debug_export_rag_report', { testId: 'SELFTEST', title: 'Self test', route: '/x', syncToCanvasDir: false,
    testCases: [{ id: 'TC-1', title: 'ok', status: 'passed' }, { id: 'TC-2', title: 'ko', status: 'failed' }] });
  const canvas = JSON.parse(fs.readFileSync(r.obsidianCanvasPath, 'utf8'));
  const ids = new Set(canvas.nodes.map((n) => n.id));
  assert.ok(canvas.nodes.every((n) => [n.x, n.y, n.width, n.height].every(Number.isFinite)));
  assert.ok(canvas.edges.every((e) => ids.has(e.fromNode) && ids.has(e.toNode)));
  const md = fs.readFileSync(r.mdPath, 'utf8');
  assert.doesNotMatch(md, /orders\.service\.ts|142|180ms|Protected/);
  for (const p of [r.mdPath, r.jsonPath, r.obsidianCanvasPath]) fs.rmSync(p, { force: true });
});

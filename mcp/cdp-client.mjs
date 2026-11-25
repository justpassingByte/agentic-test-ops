/**
 * Chrome DevTools Protocol (CDP) Autonomous Debugger Client
 * Connects directly to Node.js --inspect WebSocket endpoint to programmatically
 * control breakpoints, catch exceptions, and evaluate live heap variables.
 *
 * Notes:
 * - Web frameworks (Express, NestJS, Fastify) CATCH handler errors and answer HTTP 500,
 *   so V8 treats them as caught exceptions. 'uncaught' alone misses them; the default is
 *   therefore 'all', with exceptions thrown inside node_modules / node internals skipped
 *   (auto-resumed) so only application frames are reported.
 * - When a package manager (npm/pnpm/yarn) is launched with NODE_OPTIONS=--inspect, the
 *   package manager itself grabs the inspect port and the real app runs WITHOUT an
 *   inspector. Such targets are rejected with an explanatory error.
 * - Requires Node.js >= 22 (global WebSocket).
 */

import { spawn } from 'node:child_process';

const PACKAGE_MANAGER_TARGET = /(npm-cli|npx-cli|pnpm|yarn)(\.c?js)?/i;

function truncate(text, max = 3000) {
  const s = String(text || '').trim();
  return s.length <= max ? s : `${s.slice(0, max / 2)}\n... [truncated ${s.length - max} chars] ...\n${s.slice(-max / 2)}`;
}

function isLibraryOrInternalUrl(url) {
  return !url || url.startsWith('node:') || /[\\/]node_modules[\\/]/.test(url);
}

function escapeRegex(str) {
  return String(str).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function pickTarget(targets, targetFilter) {
  if (targetFilter) {
    const needle = String(targetFilter).toLowerCase();
    return targets.find(t => `${t.title} ${t.url} ${t.id}`.toLowerCase().includes(needle)) || null;
  }
  return targets.find(t => !PACKAGE_MANAGER_TARGET.test(`${t.title} ${t.url}`)) || null;
}

export async function runCdpInspection({
  inspectPort = 9229,
  timeoutMs = 15000,
  pauseOnExceptions = 'all',
  includeLibraryExceptions = false,
  exceptionFilter,
  targetFilter,
  expressions = [],
  breakpoints = [],
  trigger
} = {}) {
  if (typeof WebSocket === 'undefined') {
    throw new Error(`debug_inspect_cdp requires Node.js >= 22 (global WebSocket). Current runtime: ${process.version}`);
  }

  // 1. Query Node inspect target list
  const listRes = await fetch(`http://127.0.0.1:${inspectPort}/json/list`);
  if (!listRes.ok) {
    throw new Error(`Failed to query inspect port ${inspectPort}: HTTP ${listRes.status}`);
  }
  const targets = await listRes.json();
  if (!Array.isArray(targets) || targets.length === 0) {
    throw new Error(`No active Node.js inspect targets found on port ${inspectPort}`);
  }

  const target = pickTarget(targets, targetFilter);
  if (!target) {
    const titles = targets.map(t => t.title || t.url).join(', ');
    throw new Error(
      targetFilter
        ? `No inspect target on port ${inspectPort} matches "${targetFilter}". Available: ${titles}`
        : `Inspect port ${inspectPort} is held by a package-manager process (${titles}), so the application itself has no inspector. ` +
          `Put --inspect on the final node command (e.g. "node --inspect=127.0.0.1:${inspectPort} dist/main.js" or "tsx --inspect=127.0.0.1:${inspectPort} src/main.ts") instead of NODE_OPTIONS on npm/pnpm.`
    );
  }
  if (!target.webSocketDebuggerUrl) {
    throw new Error(`Target on port ${inspectPort} does not expose webSocketDebuggerUrl (another debugger may already be attached)`);
  }

  return new Promise((resolve, reject) => {
    const ws = new WebSocket(target.webSocketDebuggerUrl);
    let reqId = 1;
    let settled = false;
    let skippedLibraryExceptions = 0;
    let skippedFilteredExceptions = 0;
    const filterRegex = exceptionFilter ? new RegExp(exceptionFilter, 'i') : null;
    const pendingEvals = new Map();
    const evaluatedVars = {};
    // CallFrame.url is deprecated and empty for ES modules: resolve file URLs through scriptId.
    const scriptUrls = new Map();
    const frameUrl = (f) => f?.url || scriptUrls.get(f?.location?.scriptId) || '';
    let capturedPause = null;

    const send = (method, params) => {
      const id = reqId++;
      ws.send(JSON.stringify(params ? { id, method, params } : { id, method }));
      return id;
    };
    // Request/response helper for setup calls that need the CDP reply.
    const pendingCalls = new Map();
    const call = (method, params) => new Promise((res) => pendingCalls.set(send(method, params), res));
    const breakpointsResolved = [];

    // Release every handler and the socket so repeated inspections never accumulate listeners.
    const cleanup = () => {
      clearTimeout(timer);
      ws.onopen = ws.onmessage = ws.onerror = ws.onclose = null;
      try { ws.close(); } catch {}
    };

    // Optional trigger: a command that reproduces the failure, started only AFTER the debugger is attached
    // and breakpoints are set, so a single tool call both reproduces the bug and captures its runtime state.
    let triggerResult = null;
    let triggerDone = null;
    const runTrigger = () => {
      const t = typeof trigger === 'string' ? { command: trigger } : trigger;
      const started = Date.now();
      let output = '';
      const child = spawn(t.command, { cwd: t.cwd || process.cwd(), shell: true, env: process.env });
      child.stdout.on('data', (d) => { output += d; });
      child.stderr.on('data', (d) => { output += d; });
      triggerDone = new Promise((res) => {
        const killTimer = setTimeout(() => { try { child.kill(); } catch {} }, t.timeoutMs || timeoutMs);
        child.on('exit', (code) => {
          clearTimeout(killTimer);
          triggerResult = { command: t.command, exitCode: code, durationMs: Date.now() - started, output: truncate(output) };
          res();
          // Trigger finished without hitting any pause: no need to wait for the full timeout.
          if (!capturedPause) setTimeout(() => finish({ status: 'CLEAN_NO_EXCEPTION', message: 'Trigger finished without pausing at a breakpoint or application exception.' }), 1000);
        });
      });
    };

    const finish = async (result) => {
      if (settled) return;
      settled = true;
      // Guarantee the Node runtime is unpaused before disconnecting.
      try {
        if (ws.readyState === WebSocket.OPEN) {
          send('Debugger.resume');
          send('Debugger.disable');
        }
      } catch {}
      // Let the trigger complete after resuming so its output (e.g. the HTTP status the test saw) is part of the result.
      if (triggerDone) await Promise.race([triggerDone, new Promise((r) => setTimeout(r, timeoutMs))]);
      setTimeout(cleanup, 100);
      resolve({ target: { title: target.title, url: target.url }, skippedLibraryExceptions, skippedFilteredExceptions,
        ...(breakpointsResolved.length ? { breakpointsResolved } : {}), ...result, ...(triggerResult ? { trigger: triggerResult } : {}) });
    };

    const pausedResult = () => ({
      status: 'PAUSED',
      reason: capturedPause.reason,
      exception: capturedPause.exception,
      topFrame: capturedPause.topFrame,
      callStack: capturedPause.callStack,
      evaluatedVariables: evaluatedVars
    });

    const timer = setTimeout(() => {
      finish(capturedPause ? pausedResult() : {
        status: 'CLEAN_NO_EXCEPTION',
        message: `Inspect session ran for ${timeoutMs}ms without pausing on an application exception (mode: ${pauseOnExceptions}).`
      });
    }, timeoutMs);

    ws.onopen = async () => {
      await call('Debugger.enable');   // scriptParsed events for already-loaded scripts arrive before this reply
      send('Runtime.enable');
      if (pauseOnExceptions && pauseOnExceptions !== 'none') {
        send('Debugger.setPauseOnExceptions', { state: pauseOnExceptions });
      }
      for (const bp of Array.isArray(breakpoints) ? breakpoints : []) {
        if (bp.match) {
          // Source-text breakpoint: works on transpiled/minified code (tsx, ts-node, bundlers) where the
          // original line numbers do not exist in the script V8 actually runs.
          const file = String(bp.file || '').replace(/\\/g, '/');
          const entry = [...scriptUrls.entries()].find(([, url]) => url.includes(file));
          if (!entry) { breakpointsResolved.push({ file, match: bp.match, resolved: false, reason: 'script not loaded' }); continue; }
          const src = (await call('Debugger.getScriptSource', { scriptId: entry[0] })).result?.scriptSource || '';
          const idx = src.indexOf(bp.match);
          if (idx < 0) { breakpointsResolved.push({ file, match: bp.match, resolved: false, reason: 'text not found in loaded script' }); continue; }
          const before = src.slice(0, idx);
          const lineNumber = before.split('\n').length - 1;
          const columnNumber = idx - (before.lastIndexOf('\n') + 1);
          const r = await call('Debugger.setBreakpoint', { location: { scriptId: entry[0], lineNumber, columnNumber } });
          breakpointsResolved.push({ file, match: bp.match, resolved: Boolean(r.result?.breakpointId), url: entry[1], generatedLine: lineNumber + 1, generatedColumn: columnNumber + 1 });
        } else {
          const r = await call('Debugger.setBreakpointByUrl', {
            urlRegex: bp.urlRegex || escapeRegex(bp.file || ''),
            lineNumber: (bp.line || 1) - 1,
            ...(bp.column ? { columnNumber: bp.column - 1 } : {})
          });
          breakpointsResolved.push({ file: bp.file, line: bp.line, resolved: (r.result?.locations || []).length > 0 });
        }
      }
      if (trigger) runTrigger();
    };

    ws.onmessage = (event) => {
      let msg;
      try { msg = JSON.parse(event.data); } catch { return; }

      if (msg.id && pendingCalls.has(msg.id)) {
        pendingCalls.get(msg.id)(msg);
        pendingCalls.delete(msg.id);
        return;
      }

      if (msg.method === 'Debugger.scriptParsed') {
        if (msg.params?.url) scriptUrls.set(msg.params.scriptId, msg.params.url);
        return;
      }

      if (msg.method === 'Debugger.paused') {
        if (capturedPause) {
          // Already captured one pause; let any further pause continue.
          send('Debugger.resume');
          return;
        }
        const callFrames = msg.params?.callFrames || [];
        const topFrame = callFrames[0] || {};
        const isException = msg.params?.reason === 'exception' || msg.params?.reason === 'promiseRejection';

        if (isException && !includeLibraryExceptions && isLibraryOrInternalUrl(frameUrl(topFrame))) {
          skippedLibraryExceptions++;
          send('Debugger.resume');
          return;
        }
        // Exceptions that are thrown and caught as normal control flow (e.g. inside a JWT library) are noise:
        // with exceptionFilter, keep running until the exception text matches.
        if (isException && filterRegex && !filterRegex.test(msg.params?.data?.description || '')) {
          skippedFilteredExceptions++;
          send('Debugger.resume');
          return;
        }

        const exceptionData = msg.params?.data;
        capturedPause = {
          reason: msg.params?.reason || 'unknown',
          exception: exceptionData ? {
            type: exceptionData.type,
            description: exceptionData.description,
            className: exceptionData.className
          } : null,
          topFrame: {
            functionName: topFrame.functionName || '(anonymous)',
            url: frameUrl(topFrame),
            line: (topFrame.location?.lineNumber || 0) + 1,
            column: (topFrame.location?.columnNumber || 0) + 1
          },
          callStack: callFrames.slice(0, 8).map(f => ({
            functionName: f.functionName || '(anonymous)',
            url: frameUrl(f),
            line: (f.location?.lineNumber || 0) + 1,
            column: (f.location?.columnNumber || 0) + 1
          }))
        };

        if (expressions.length > 0 && topFrame.callFrameId) {
          for (const expr of expressions) {
            const id = send('Debugger.evaluateOnCallFrame', {
              callFrameId: topFrame.callFrameId,
              expression: expr,
              returnByValue: true
            });
            pendingEvals.set(id, expr);
          }
        } else {
          finish(pausedResult());
        }
        return;
      }

      if (msg.id && pendingEvals.has(msg.id)) {
        const expr = pendingEvals.get(msg.id);
        pendingEvals.delete(msg.id);
        const result = msg.result?.result;
        evaluatedVars[expr] = result ? {
          type: result.type,
          value: result.value !== undefined ? result.value : result.description,
          unserializable: result.unserializableValue
        } : { error: msg.error?.message || 'evaluation failed' };

        if (pendingEvals.size === 0 && capturedPause) {
          finish(pausedResult());
        }
      }
    };

    ws.onerror = (err) => {
      if (settled) return;
      settled = true;
      cleanup();
      reject(new Error(`CDP WebSocket error: ${err?.message || 'connection failed'}`));
    };
  });
}

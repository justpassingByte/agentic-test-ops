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

// ---- Source maps (tsx / ts-node / bundlers) ----------------------------------------------
// tsx compiles each .ts file to a few long lines and attaches an inline source map, so a
// breakpoint on a TypeScript line only binds if it is translated through that map.
const B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
const B64_INDEX = Object.fromEntries([...B64].map((c, i) => [c, i]));

function decodeVlqSegment(segment) {
  const values = [];
  let value = 0, shift = 0;
  for (const ch of segment) {
    const digit = B64_INDEX[ch];
    if (digit === undefined) return null;
    value += (digit & 31) << shift;
    if (digit & 32) { shift += 5; continue; }
    values.push(value & 1 ? -(value >>> 1) : value >>> 1);
    value = 0; shift = 0;
  }
  return values;
}

/** Returns [{genLine, genCol, srcIdx, srcLine, srcCol}] (all 0-based). */
export function decodeSourceMapMappings(mappings) {
  const out = [];
  let srcIdx = 0, srcLine = 0, srcCol = 0;
  String(mappings || '').split(';').forEach((lineStr, genLine) => {
    let genCol = 0;
    for (const seg of lineStr.split(',')) {
      if (!seg) continue;
      const v = decodeVlqSegment(seg);
      if (!v || v.length === 0) continue;
      genCol += v[0];
      if (v.length >= 4) {
        srcIdx += v[1]; srcLine += v[2]; srcCol += v[3];
        out.push({ genLine, genCol, srcIdx, srcLine, srcCol });
      }
    }
  });
  return out;
}

async function loadSourceMap(sourceMapURL, scriptUrl) {
  if (!sourceMapURL) return null;
  try {
    if (sourceMapURL.startsWith('data:')) {
      const comma = sourceMapURL.indexOf(',');
      const meta = sourceMapURL.slice(5, comma);
      const body = sourceMapURL.slice(comma + 1);
      const text = meta.includes('base64') ? Buffer.from(body, 'base64').toString('utf8') : decodeURIComponent(body);
      return JSON.parse(text);
    }
    const { readFile } = await import('node:fs/promises');
    const { fileURLToPath } = await import('node:url');
    const mapUrl = new URL(sourceMapURL, scriptUrl);
    if (mapUrl.protocol !== 'file:') return null;
    return JSON.parse(await readFile(fileURLToPath(mapUrl), 'utf8'));
  } catch {
    return null;
  }
}

/** First generated position whose original line is `line` (1-based) in the source ending with `file`. */
export function generatedPositionFor(map, file, line) {
  const sources = (map?.sources || []).map(s => String(s).replace(/\\/g, '/'));
  const base = String(file || '').replace(/\\/g, '/').split('/').pop();
  let srcIdx = sources.findIndex(s => s.endsWith(String(file).replace(/\\/g, '/')));
  if (srcIdx < 0) srcIdx = sources.findIndex(s => s.endsWith(base));
  if (srcIdx < 0 && sources.length === 1) srcIdx = 0;
  if (srcIdx < 0) return null;
  const hits = decodeSourceMapMappings(map.mappings)
    .filter(m => m.srcIdx === srcIdx && m.srcLine === line - 1)
    .sort((a, b) => a.genLine - b.genLine || a.genCol - b.genCol);
  return hits[0] || null;
}

/** Original position (1-based line) for a generated position (0-based), or null. */
export function originalPositionFor(map, genLine, genCol) {
  let best = null;
  for (const m of decodeSourceMapMappings(map?.mappings)) {
    if (m.genLine !== genLine || m.genCol > genCol) continue;
    if (!best || m.genCol >= best.genCol) best = m;
  }
  return best ? { source: map.sources?.[best.srcIdx], line: best.srcLine + 1, column: best.srcCol + 1 } : null;
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
    const scriptSourceMaps = new Map();
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
      // Translate paused frames back to the original (TypeScript) lines through source maps.
      for (const f of [result?.topFrame, ...(result?.callStack || [])]) {
        if (!f || f._scriptId === undefined) continue;
        const map = await loadSourceMap(scriptSourceMaps.get(f._scriptId), f.url);
        const orig = map ? originalPositionFor(map, f.line - 1, f.column - 1) : null;
        if (orig) f.sourceLine = orig.line;
        delete f._scriptId;
      }
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
      // Application scripts only (no node_modules / node: internals), matched by path fragment.
      const appScripts = (file) => {
        const frag = String(file || '').replace(/\\/g, '/');
        return [...scriptUrls.entries()]
          .filter(([, url]) => !isLibraryOrInternalUrl(url))
          .filter(([, url]) => !frag || decodeURIComponent(url).replace(/\\/g, '/').includes(frag));
      };
      const notLoadedHint = (file) => {
        const base = String(file || '').replace(/\\/g, '/').split('/').pop();
        const near = [...scriptUrls.values()].filter(u => base && u.includes(base)).slice(0, 5);
        return near.length ? `Loaded scripts with a similar name: ${near.join(', ')}` :
          'No loaded application script has this path; check the fragment (e.g. "listings/listings.repo.ts").';
      };

      for (const bp of Array.isArray(breakpoints) ? breakpoints : []) {
        if (bp.match) {
          // Source-text breakpoint: pause at the first occurrence of the text in the code V8 runs.
          // Without `file`, every loaded application script is searched.
          const candidates = appScripts(bp.file);
          if (candidates.length === 0) {
            breakpointsResolved.push({ file: bp.file || '', match: bp.match, resolved: false, reason: 'script not loaded', hint: notLoadedHint(bp.file) });
            continue;
          }
          let placed = null;
          let matchedScripts = 0;
          for (const [scriptId, url] of candidates) {
            const src = (await call('Debugger.getScriptSource', { scriptId })).result?.scriptSource || '';
            const idx = src.indexOf(bp.match);
            if (idx < 0) continue;
            matchedScripts++;
            if (placed) continue;
            const before = src.slice(0, idx);
            const lineNumber = before.split('\n').length - 1;
            const columnNumber = idx - (before.lastIndexOf('\n') + 1);
            const r = await call('Debugger.setBreakpoint', { location: { scriptId, lineNumber, columnNumber } });
            placed = { resolved: Boolean(r.result?.breakpointId), url, generatedLine: lineNumber + 1, generatedColumn: columnNumber + 1 };
          }
          if (!placed) {
            breakpointsResolved.push({
              file: bp.file || '', match: bp.match, resolved: false,
              reason: `text not found in ${candidates.length} loaded script(s)`,
              hint: 'The transpiler may have reformatted this text (spacing, quotes, template literals). Use a shorter fragment such as an identifier or function call, or use {file, line} with the TypeScript line number.'
            });
            continue;
          }
          breakpointsResolved.push({
            file: bp.file || '', match: bp.match, ...placed,
            ...(matchedScripts > 1 ? { warning: `text occurs in ${matchedScripts} scripts; breakpoint placed in the first. Add "file" to choose.` } : {})
          });
        } else {
          // Line breakpoint on the ORIGINAL source line. When the script carries a source map
          // (tsx, ts-node, bundlers) the line is translated through it; otherwise it is used as-is.
          const candidates = appScripts(bp.file);
          if (candidates.length === 0) {
            breakpointsResolved.push({ file: bp.file, line: bp.line, resolved: false, reason: 'script not loaded', hint: notLoadedHint(bp.file) });
            continue;
          }
          const [scriptId, url] = candidates[0];
          const map = await loadSourceMap(scriptSourceMaps.get(scriptId), url);
          if (map) {
            const pos = generatedPositionFor(map, bp.file || url, bp.line || 1);
            if (!pos) {
              breakpointsResolved.push({ file: bp.file, line: bp.line, resolved: false, url, reason: 'no executable code on this line in the source map', hint: 'Pick a line that contains an expression or statement (not a blank line, comment or a lone bracket).' });
              continue;
            }
            const r = await call('Debugger.setBreakpoint', { location: { scriptId, lineNumber: pos.genLine, columnNumber: pos.genCol } });
            breakpointsResolved.push({ file: bp.file, line: bp.line, resolved: Boolean(r.result?.breakpointId), url, via: 'source map', generatedLine: pos.genLine + 1, generatedColumn: pos.genCol + 1 });
          } else {
            const r = await call('Debugger.setBreakpoint', {
              location: { scriptId, lineNumber: (bp.line || 1) - 1, ...(bp.column ? { columnNumber: bp.column - 1 } : {}) }
            });
            breakpointsResolved.push({ file: bp.file, line: bp.line, resolved: Boolean(r.result?.breakpointId), url, via: 'direct (no source map)' });
          }
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
        if (msg.params?.sourceMapURL) scriptSourceMaps.set(msg.params.scriptId, msg.params.sourceMapURL);
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
            column: (topFrame.location?.columnNumber || 0) + 1,
            _scriptId: topFrame.location?.scriptId
          },
          callStack: callFrames.slice(0, 8).map(f => ({
            functionName: f.functionName || '(anonymous)',
            url: frameUrl(f),
            line: (f.location?.lineNumber || 0) + 1,
            column: (f.location?.columnNumber || 0) + 1,
            _scriptId: f.location?.scriptId
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

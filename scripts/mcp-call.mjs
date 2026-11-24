#!/usr/bin/env node
/**
 * Minimal MCP stdio client for the Agentic TestOps `debug-controller` server.
 *
 * Speaks the same JSON-RPC 2.0 protocol an AI host (Claude Code, Gemini CLI, Antigravity) uses:
 * initialize -> notifications/initialized -> tools/call. One invocation = one real tool call.
 *
 * Usage:
 *   node scripts/mcp-call.mjs --list
 *   node scripts/mcp-call.mjs <toolName> '<json arguments>'
 *   node scripts/mcp-call.mjs <toolName> @path/to/args.json
 *
 * Exit code: 0 if the tool returned isError=false, 1 otherwise.
 */
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const SERVER = path.resolve(import.meta.dirname, '..', 'mcp', 'server.mjs');
const [toolName, rawArgs = '{}'] = process.argv.slice(2);

if (!toolName) {
  console.error('Usage: node scripts/mcp-call.mjs <toolName> \'<json>\' | @file.json | --list');
  process.exit(2);
}

const args = toolName === '--list' ? {} : JSON.parse(rawArgs.startsWith('@') ? fs.readFileSync(rawArgs.slice(1), 'utf8') : rawArgs);
const server = spawn(process.execPath, [SERVER], { stdio: ['pipe', 'pipe', 'inherit'] });

let buffer = '';
const pending = new Map();
server.stdout.on('data', (chunk) => {
  buffer += chunk;
  let nl;
  while ((nl = buffer.indexOf('\n')) >= 0) {
    const line = buffer.slice(0, nl).trim();
    buffer = buffer.slice(nl + 1);
    if (!line) continue;
    const msg = JSON.parse(line);
    pending.get(msg.id)?.(msg);
    pending.delete(msg.id);
  }
});

let nextId = 1;
function request(method, params) {
  const id = nextId++;
  return new Promise((resolve) => {
    pending.set(id, resolve);
    server.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
  });
}

const init = await request('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'mcp-call', version: '1.0.0' } });
server.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) + '\n');

let exitCode = 0;
if (toolName === '--list') {
  const res = await request('tools/list', {});
  console.log(`${init.result.serverInfo.name} ${init.result.serverInfo.version}: ${res.result.tools.length} tools`);
  for (const t of res.result.tools) console.log(`- ${t.name}`);
} else {
  const res = await request('tools/call', { name: toolName, arguments: args });
  const result = res.result || {};
  for (const part of result.content || []) if (part.type === 'text') console.log(part.text);
  if (res.error) console.log(JSON.stringify(res.error));
  exitCode = result.isError || res.error ? 1 : 0;
}

server.stdin.end();
server.kill();
process.exit(exitCode);

#!/usr/bin/env node
/**
 * Open a source file in VS Code at the line containing a given code snippet.
 *
 *   node scripts/open-in-vscode.mjs <file> "<code snippet>" [--dry-run]
 *
 * Used by the demo: debug_inspect_cdp pauses on transpiled code (tsx), so the TypeScript line is
 * recovered by searching the original .ts file on disk for the same snippet.
 */
import { spawnSync, spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

function findCodeCli() {
  if (process.env.CODE_CLI && fs.existsSync(process.env.CODE_CLI)) return process.env.CODE_CLI;
  const which = spawnSync(process.platform === 'win32' ? 'where' : 'which', ['code'], { encoding: 'utf8' });
  const onPath = which.status === 0 && which.stdout.split(/\r?\n/).find(Boolean);
  if (onPath) return onPath.trim();
  const candidates = [
    path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Microsoft VS Code', 'bin', 'code.cmd'),
    path.join(process.env.ProgramFiles || '', 'Microsoft VS Code', 'bin', 'code.cmd'),
  ];
  return candidates.find((c) => fs.existsSync(c)) || null;
}

/** Returns { file, line, column } (1-based) of the first line containing `snippet`. */
export function locate(file, snippet) {
  const lines = fs.readFileSync(file, 'utf8').split(/\r?\n/);
  const idx = lines.findIndex((l) => l.includes(snippet));
  if (idx < 0) throw new Error(`"${snippet}" not found in ${file}`);
  return { file, line: idx + 1, column: lines[idx].indexOf(snippet) + 1 };
}

export function openAtSnippet(file, snippet, { dryRun = false } = {}) {
  const loc = locate(file, snippet);
  const target = `${loc.file}:${loc.line}:${loc.column}`;
  const cli = findCodeCli();
  if (dryRun || !cli) return { ...loc, opened: false, reason: cli ? 'dry-run' : 'VS Code CLI not found (set CODE_CLI)' };
  // .cmd launchers need a shell; with shell:true Node does not quote, and the default path contains spaces.
  const isCmd = cli.toLowerCase().endsWith('.cmd');
  const child = isCmd
    ? spawn(`"${cli}" -g "${target}"`, { stdio: 'ignore', detached: true, shell: true })
    : spawn(cli, ['-g', target], { stdio: 'ignore', detached: true });
  child.unref();
  return { ...loc, opened: true };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [file, snippet] = process.argv.slice(2).filter((a) => !a.startsWith('--'));
  if (!file || !snippet) {
    console.error('Usage: node scripts/open-in-vscode.mjs <file> "<code snippet>" [--dry-run]');
    process.exit(2);
  }
  const f = file.startsWith('file:') ? fileURLToPath(file) : file;
  console.log(JSON.stringify(openAtSnippet(f, snippet, { dryRun: process.argv.includes('--dry-run') })));
}

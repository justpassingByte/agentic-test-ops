// -*- coding: utf-8 -*-
/**
 * AGENTIC TESTOPS - LIVE INTERACTIVE DEMO ON TRUSTBASE CUSTOMER WEB
 * Opens visible Google Chrome (slowMo: 700), interacts with real TrustBase pages,
 * asserts HTTP & DOM readiness, and saves real screenshots in ./screenshots/.
 */

import { spawn } from 'node:child_process';
import os from 'node:os';
import path from 'node:path';
import fs from 'node:fs';

let playwrightModule;
try {
  playwrightModule = await import('playwright');
} catch {
  playwrightModule = await import('./mcp/node_modules/playwright/index.mjs');
}
const { chromium } = playwrightModule;

const ROOT_DIR = import.meta.dirname;
const TRUSTBASE_URL = process.env.TRUSTBASE_CUSTOMER_URL || 'http://localhost:4200';
const CUSTOMER_DIR = process.env.TRUSTBASE_CUSTOMER_DIR ||
  path.join(os.homedir(), 'Documents', 'trustbase', 'trustbase-project', 'customer');
const SCREENSHOTS_DIR = path.join(ROOT_DIR, 'screenshots');

async function ensureServerRunning() {
  console.log(`[1/5] Kiem tra may chu TrustBase Customer (${TRUSTBASE_URL})...`);
  try {
    const res = await fetch(TRUSTBASE_URL, { signal: AbortSignal.timeout(3000) });
    if (res.status < 500) {
      console.log(`      OK: Dang hoat dong tai ${TRUSTBASE_URL}`);
      return;
    }
  } catch {
    // Server not yet listening
  }

  if (!fs.existsSync(CUSTOMER_DIR)) {
    throw new Error(`Khong tim thay thu muc Customer SUT tai: ${CUSTOMER_DIR}`);
  }

  console.log(`      -> Dang khoi dong Customer Dev Server tai ${CUSTOMER_DIR}...`);
  const devProcess = spawn(process.platform === 'win32' ? 'cmd.exe' : 'sh', [process.platform === 'win32' ? '/c' : '-c', 'pnpm dev'], {
    cwd: CUSTOMER_DIR,
    stdio: 'ignore',
    detached: true
  });
  devProcess.unref();

  for (let i = 0; i < 30; i++) {
    await new Promise(r => setTimeout(r, 1000));
    try {
      const res = await fetch(TRUSTBASE_URL, { signal: AbortSignal.timeout(1000) });
      if (res.status < 500) {
        console.log('      OK: May chu TrustBase da san sang!');
        return;
      }
    } catch {}
  }
  throw new Error('Timeout 30s cho TrustBase Customer Server khoi dong.');
}

async function runRealDemo() {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
  await ensureServerRunning();

  console.log('\n===================================================================');
  console.log('   KHOI DONG GOOGLE CHROME - DEMO KIEM THU WEB THUC TE (NO CAP)');
  console.log('===================================================================\n');

  const browser = await chromium.launch({
    channel: 'chrome',
    headless: false,
    slowMo: 700
  });

  const context = await browser.newContext({ viewport: { width: 1300, height: 850 } });
  const page = await context.newPage();

  const failedRequests = [];
  page.on('response', resp => {
    if (resp.status() >= 500) {
      failedRequests.push({ url: resp.url(), status: resp.status() });
    }
  });

  try {
    // 1. Trang chu
    console.log(`[Kich ban 1] Mo Trang chu: ${TRUSTBASE_URL}/vi`);
    await page.goto(`${TRUSTBASE_URL}/vi`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    console.log('      Title:', await page.title());
    await page.evaluate(() => window.scrollBy({ top: 350, behavior: 'smooth' }));
    await page.waitForTimeout(900);
    await page.evaluate(() => window.scrollBy({ top: -350, behavior: 'smooth' }));
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'real_01_trang_chu.png') });

    // 2. Marketplace
    console.log('\n[Kich ban 2] Marketplace (/vi/marketplace)');
    await page.goto(`${TRUSTBASE_URL}/vi/marketplace`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    const searchInput = page.locator('#marketplace-search-input');
    if (await searchInput.count() > 0) {
      await searchInput.fill('Steam');
      const searchBtn = page.locator('button:has-text("Tìm kiếm")');
      if (await searchBtn.count() > 0) await searchBtn.click();
    }
    await page.waitForTimeout(1200);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'real_02_marketplace.png') });

    // 3. Sign up form
    console.log('\n[Kich ban 3] Bieu mau Dang ky (/vi/sign-up)');
    await page.goto(`${TRUSTBASE_URL}/vi/sign-up`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.locator('#fullName').fill('Nguyễn Hữu Thắng (QA Test Lead)');
    await page.locator('#username').fill('nhom05_testops');
    await page.locator('#email').fill('nhom05.qa@trustbase.vn');
    await page.locator('#password').fill('P@ssw0rd2026!Secure');
    await page.waitForTimeout(900);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'real_03_dang_ky_form.png') });

    // 4. Bang phi & Escrow
    console.log('\n[Kich ban 4] Bang phi & Co che Escrow (/vi/fees)');
    await page.goto(`${TRUSTBASE_URL}/vi/fees`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.evaluate(() => window.scrollBy({ top: 300, behavior: 'smooth' }));
    await page.waitForTimeout(1200);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'real_04_bang_phi_escrow.png') });

    console.log(`\nHTTP >= 500 detected during walkthrough: ${failedRequests.length}`);
    console.log('Giu cua so trinh duyet 5 giay de quan sat...');
    await page.waitForTimeout(5000);
  } finally {
    await context.close();
    await browser.close();
  }
}

runRealDemo().catch(err => {
  console.error('[FAIL] Loi khi chay demo thuc te:', err.message);
  process.exit(1);
});

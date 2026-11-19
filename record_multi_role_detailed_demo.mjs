// -*- coding: utf-8 -*-
/**
 * AGENTIC TESTOPS - VERIFIED NON-CAP MULTI-ROLE E2E RUNNER (Buyer -> Seller -> Admin)
 * - Strictly asserts real DOM, URL, and HTTP API outcomes at every stage (never fakes success overlays).
 * - Launches visible Chrome (headless: false) so observers can watch real browser interactions.
 * - Saves verified step screenshots into ./screenshots/.
 * - Optional: pass `--record-video` (or RECORD_VIDEO=1) only if you explicitly want a .webm recording.
 */

import path from 'node:path';
import fs from 'node:fs';
import process from 'node:process';

let playwrightModule;
try {
  playwrightModule = await import('playwright');
} catch {
  playwrightModule = await import('./mcp/node_modules/playwright/index.mjs');
}
const { chromium } = playwrightModule;

const ROOT_DIR = import.meta.dirname;
const SCREENSHOTS_DIR = path.join(ROOT_DIR, 'screenshots');
const RECORD_VIDEO = process.argv.includes('--record-video') || process.env.RECORD_VIDEO === '1';
const VIDEOS_DIR = path.join(ROOT_DIR, 'videos');

const CUSTOMER_BASE = process.env.TRUSTBASE_CUSTOMER_URL || 'http://localhost:4200';
const API_BASE = process.env.TRUSTBASE_API_URL || 'http://localhost:4201';
const ADMIN_BASE = process.env.TRUSTBASE_ADMIN_URL || 'http://localhost:4203';

fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
if (RECORD_VIDEO) {
  fs.mkdirSync(VIDEOS_DIR, { recursive: true });
}

function assertOk(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

async function checkServiceReachable(name, url) {
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(4000) });
    return { name, url, up: res.status < 500, status: res.status };
  } catch (err) {
    return { name, url, up: false, error: err.message };
  }
}

async function updateOverlay(page, roleTag, title, stepDesc, color = '#38bdf8') {
  try {
    await page.evaluate(({ roleTag, title, stepDesc, color }) => {
      let box = document.getElementById('agentic-live-overlay');
      if (!box) {
        box = document.createElement('div');
        box.id = 'agentic-live-overlay';
        box.style.position = 'fixed';
        box.style.top = '15px';
        box.style.right = '20px';
        box.style.zIndex = '9999999';
        box.style.background = 'rgba(15, 23, 42, 0.95)';
        box.style.color = '#fff';
        box.style.padding = '14px 18px';
        box.style.borderRadius = '10px';
        box.style.boxShadow = '0 10px 30px rgba(0,0,0,0.55)';
        box.style.fontFamily = 'Segoe UI, Roboto, sans-serif';
        box.style.fontSize = '13px';
        box.style.maxWidth = '450px';
        box.style.lineHeight = '1.45';
        document.body.appendChild(box);
      }
      box.style.borderLeft = `5px solid ${color}`;
      box.innerHTML = `
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.4px;color:${color};font-weight:800;margin-bottom:4px;">${roleTag}</div>
        <div style="font-size:14px;font-weight:700;color:#ffffff;margin-bottom:5px;">${title}</div>
        <div style="color:#cbd5e1;font-size:12.5px;">${stepDesc}</div>
      `;
    }, { roleTag, title, stepDesc, color });
  } catch {
    // Ignore overlay errors during navigation transitions
  }
}

async function loginApi(emailOrPhone, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ emailOrPhone, password })
  });
  const json = await res.json().catch(() => null);
  return { status: res.status, token: json?.data?.accessToken || null, raw: json };
}

async function runVerifiedMultiRoleE2E() {
  console.log('\n=======================================================================');
  console.log(' AGENTIC TESTOPS - VERIFIED MULTI-ROLE E2E RUNNER (NO FAKE OVERLAYS)');
  console.log('=======================================================================\n');

  // 0. Pre-flight check on TrustBase SUT services
  const checks = await Promise.all([
    checkServiceReachable('Customer Web', `${CUSTOMER_BASE}/vi`),
    checkServiceReachable('Backend API', `${API_BASE}/health`),
    checkServiceReachable('Admin Console', `${ADMIN_BASE}/login`)
  ]);
  for (const c of checks) {
    console.log(`[PRE-FLIGHT] ${c.name} (${c.url}): ${c.up ? `UP (${c.status})` : `DOWN (${c.error || c.status})`}`);
  }
  const down = checks.filter(c => !c.up);
  if (down.length > 0) {
    throw new Error(
      `TrustBase services offline (${down.map(d => d.name).join(', ')}). Start API (4201), Customer (4200), and Admin (4203) before running live demo.`
    );
  }

  // 1. Authenticate Buyer & Seller via API
  const buyerAuth = await loginApi('customer1@trustbase.local', 'demo1234');
  assertOk(buyerAuth.token, `Buyer login failed (HTTP ${buyerAuth.status})`);
  const sellerAuth = await loginApi('seller1@trustbase.local', 'demo1234');
  assertOk(sellerAuth.token, `Seller login failed (HTTP ${sellerAuth.status})`);

  const browser = await chromium.launch({
    channel: 'chrome',
    headless: false,
    slowMo: 450
  });

  const contextOptions = { viewport: { width: 1280, height: 760 } };
  if (RECORD_VIDEO) {
    contextOptions.recordVideo = { dir: VIDEOS_DIR, size: { width: 1280, height: 760 } };
  }
  const context = await browser.newContext(contextOptions);
  const page = await context.newPage();

  const summary = { buyer: 'PENDING', seller: 'PENDING', admin: 'PENDING' };

  try {
    // -----------------------------------------------------------------------
    // PHASE 1: BUYER FLOW
    // -----------------------------------------------------------------------
    console.log('\n[PHASE 1] BUYER: Marketplace Search -> Checkout -> VietQR Order');
    await context.addCookies([{ name: '__tb_at', value: buyerAuth.token, domain: 'localhost', path: '/' }]);

    await page.goto(`${CUSTOMER_BASE}/vi/marketplace`, { waitUntil: 'domcontentloaded' });
    await updateOverlay(page, 'ROLE 1: BUYER', '1. Duyet Marketplace', 'Kiem tra tim kiem san pham so...', '#38bdf8');

    const searchInput = page.locator('#marketplace-search-input');
    if (await searchInput.count() > 0) {
      await searchInput.fill('Steam Wallet');
      await page.waitForTimeout(800);
    }

    await page.goto(
      `${CUSTOMER_BASE}/vi/marketplace/checkout/adefacad-56ea-49c4-be4c-2fa4ddc67d6b`,
      { waitUntil: 'domcontentloaded' }
    );
    await page.waitForTimeout(1200);

    // Fill required fields cleanly using allowed email domain so DEF-002 does not block happy path
    const nameInput = page.locator('input[name="fullName"], input#fullName').first();
    if (await nameInput.count() > 0 && !(await nameInput.inputValue())) {
      await nameInput.fill('Nguyen Huu Thang');
    }
    const emailInput = page.locator('input[name="email"], input#email').first();
    if (await emailInput.count() > 0) {
      await emailInput.fill('nhom05.buyer@gmail.com');
    }
    const phoneInput = page.locator('input[name="phone"], input#phone').first();
    if (await phoneInput.count() > 0 && !(await phoneInput.inputValue())) {
      await phoneInput.fill('0912345678');
    }
    const termsBox = page.locator('input[type="checkbox"]').first();
    if (await termsBox.count() > 0 && !(await termsBox.isChecked())) {
      await termsBox.check();
    }

    const submitBtn = page.locator('button:has-text("TẠO ĐƠN"):visible, button:has-text("Tạo đơn"):visible').first();
    assertOk((await submitBtn.count()) > 0, 'Buyer checkout button [TẠO ĐƠN] not found');

    await Promise.all([
      page.waitForURL(url => !url.toString().includes('/checkout/'), { timeout: 15000 }),
      submitBtn.click()
    ]);

    await page.waitForTimeout(1200);
    assertOk(!page.url().includes('/checkout/'), `Order creation did not leave checkout URL: ${page.url()}`);
    await updateOverlay(page, 'ROLE 1: BUYER', 'VERIFIED: Don hang Escrow da tao', `URL: ${page.url()}`, '#22c55e');
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'detailed_01_buyer_order.png') });
    summary.buyer = `PASSED (${page.url()})`;

    // -----------------------------------------------------------------------
    // PHASE 2: SELLER FLOW
    // -----------------------------------------------------------------------
    console.log('\n[PHASE 2] SELLER: Seller Studio Payouts -> Real KYC Check & Request');
    await context.clearCookies();
    await context.addCookies([{ name: '__tb_at', value: sellerAuth.token, domain: 'localhost', path: '/' }]);

    await page.goto(`${CUSTOMER_BASE}/vi/seller-dashboard/payouts`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1200);

    const kycBanner = page.locator('[data-testid="payouts-kyc-blocked-banner"]');
    if (await kycBanner.count() > 0 && await kycBanner.isVisible()) {
      await updateOverlay(page, 'ROLE 2: SELLER', 'BLOCKED: Chua xac minh eKYC', 'Nut rut tien bi khoa do seller1 chua duyet KYC trong DB/Admin Console.', '#ef4444');
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'error_02_seller_kyc_blocked.png') });
      throw new Error('Seller payout blocked by eKYC gate. Approve eKYC for seller1 in Admin/DB before testing unlocked withdrawal.');
    }

    // Target ONLY the primary withdrawal action button (never the bottom filter tab)
    const withdrawBtn = page.locator('button:has-text("Yêu cầu rút tiền ngay"):visible').first();
    assertOk((await withdrawBtn.count()) > 0, 'Primary withdraw button [Yêu cầu rút tiền ngay] not found');
    assertOk(!(await withdrawBtn.isDisabled()), 'Withdraw button is unexpectedly disabled');

    await withdrawBtn.click();
    await page.waitForTimeout(1000);

    const confirmBtn = page.locator('button:has-text("Xác nhận & Rút tiền"):visible, button:has-text("Xác nhận rút tiền"):visible').first();
    assertOk((await confirmBtn.count()) > 0, 'Payout confirmation button in modal did not appear');

    const [payoutRes] = await Promise.all([
      page.waitForResponse(r => r.url().includes('/payout') && r.request().method() === 'POST', { timeout: 15000 }),
      confirmBtn.click()
    ]);
    assertOk(payoutRes.ok(), `Seller payout request failed with HTTP ${payoutRes.status()}`);

    const pendingTab = page.locator('button:has-text("Pending"):visible').first();
    if (await pendingTab.count() > 0) {
      await pendingTab.click();
      await page.waitForTimeout(1000);
    }

    await updateOverlay(page, 'ROLE 2: SELLER', 'VERIFIED: Tao yeu cau rut tien thanh cong', `API POST HTTP ${payoutRes.status()}`, '#22c55e');
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'detailed_02_seller_payout.png') });
    summary.seller = `PASSED (HTTP ${payoutRes.status()})`;

    // -----------------------------------------------------------------------
    // PHASE 3: ADMIN FLOW
    // -----------------------------------------------------------------------
    console.log('\n[PHASE 3] ADMIN: Admin Console Login -> /money/payouts Verification');
    await context.clearCookies();
    await page.goto(`${ADMIN_BASE}/login`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(800);

    const adminEmail = process.env.TRUSTBASE_ADMIN_EMAIL || 'admin@trustbase.local';
    const candidatePasswords = [
      process.env.TRUSTBASE_ADMIN_PASSWORD,
      'Admin123!',
      'Admin@123456'
    ].filter(Boolean);

    let adminLoggedIn = false;
    let lastLoginStatus = null;

    for (const pwd of candidatePasswords) {
      await page.locator('#email').fill(adminEmail);
      await page.locator('#password').fill(pwd);
      const [loginRes] = await Promise.all([
        page.waitForResponse(r => r.url().includes('/auth/login') && r.request().method() === 'POST', { timeout: 10000 }),
        page.locator('button[type="submit"], button.btn-go').first().click()
      ]);
      lastLoginStatus = loginRes.status();
      if (loginRes.ok()) {
        adminLoggedIn = true;
        break;
      }
      await page.waitForTimeout(500);
    }

    if (!adminLoggedIn) {
      await updateOverlay(page, 'ROLE 3: ADMIN', `FAILED: Dang nhap Admin that bai (HTTP ${lastLoginStatus})`, 'Kiem tra lai mat khau admin@trustbase.local trong PostgreSQL.', '#ef4444');
      await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'error_03_admin_login_failed.png') });
      throw new Error(`Admin login failed with HTTP ${lastLoginStatus}`);
    }

    await page.waitForURL(url => !url.toString().includes('/login'), { timeout: 10000 });
    await page.goto(`${ADMIN_BASE}/money/payouts`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1200);
    assertOk(!page.url().includes('/login'), `Admin session rejected back to /login: ${page.url()}`);

    await updateOverlay(page, 'ROLE 3: ADMIN', 'VERIFIED: Da dang nhap & mo /money/payouts', `Authenticated Admin URL: ${page.url()}`, '#22c55e');
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'detailed_03_admin_payouts.png') });
    summary.admin = `PASSED (${page.url()})`;

    console.log('\nVERIFIED SUMMARY:', JSON.stringify(summary, null, 2));
  } finally {
    const videoObj = RECORD_VIDEO ? page.video() : null;
    await context.close();
    await browser.close();
    if (videoObj) {
      const rawPath = await videoObj.path();
      const target = path.join(VIDEOS_DIR, 'multi_role_e2e_verified.webm');
      fs.copyFileSync(rawPath, target);
      console.log(`Recorded optional real E2E video: ${target}`);
    }
  }
}

runVerifiedMultiRoleE2E().catch(err => {
  console.error('\n[FAIL] Multi-Role E2E verification stopped honestly:', err.message);
  process.exit(1);
});

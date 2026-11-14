import path from 'node:path';

let playwrightModule;
try {
  playwrightModule = await import('playwright');
} catch (e) {
  playwrightModule = await import('./mcp/node_modules/playwright/index.mjs');
}
const { chromium } = playwrightModule;

async function testSeller() {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  
  // 1. Authenticate Seller (seller1@trustbase.local)
  const sellerLogin = await fetch('http://localhost:4201/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ emailOrPhone: 'seller1@trustbase.local', password: 'demo1234' })
  }).then(r => r.json());

  const sellerToken = sellerLogin?.data?.accessToken;
  console.log('Seller logged in token:', sellerToken ? 'YES' : 'NO');

  const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  if (sellerToken) {
    await context.addCookies([
      { name: '__tb_at', value: sellerToken, domain: 'localhost', path: '/' }
    ]);
  }

  const page = await context.newPage();
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('response', resp => {
    if (resp.url().includes('/seller') || resp.url().includes('/payout')) {
      console.log('RESPONSE:', resp.status(), resp.url());
    }
  });

  await page.goto('http://localhost:4200/vi/seller-dashboard/payouts', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // Check if KYC banner is visible
  const kycBanner = page.locator('[data-testid="payouts-kyc-blocked-banner"]');
  console.log('KYC blocked banner count:', await kycBanner.count());

  // Find withdraw button
  const withdrawBtn = page.locator('button:has-text("Yêu cầu rút tiền"):visible, button:has-text("Rút tiền"):visible').first();
  console.log('Withdraw button text:', await withdrawBtn.innerText());
  console.log('Withdraw button disabled:', await withdrawBtn.isDisabled());

  // Click withdraw button
  await withdrawBtn.click();
  await page.waitForTimeout(1500);

  // Look for confirm button in modal
  const confirmBtn = page.locator('button:has-text("Xác nhận"), button:has-text("Gửi yêu cầu"), button:has-text("Xác nhận rút tiền")').first();
  console.log('Confirm button in modal count:', await confirmBtn.count());
  if (await confirmBtn.count() > 0) {
    console.log('Confirm button text:', await confirmBtn.innerText());
    console.log('Confirm button disabled:', await confirmBtn.isDisabled());
    await confirmBtn.click();
    await page.waitForTimeout(3000);
  }

  // Check requests tab / table
  const pendingTab = page.locator('button:has-text("Pending"), button:has-text("Chờ duyệt")').first();
  if (await pendingTab.count() > 0) {
    await pendingTab.click();
    await page.waitForTimeout(1500);
  }

  await browser.close();
}

testSeller().catch(console.error);

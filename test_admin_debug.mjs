import path from 'node:path';

let playwrightModule;
try {
  playwrightModule = await import('playwright');
} catch (e) {
  playwrightModule = await import('./mcp/node_modules/playwright/index.mjs');
}
const { chromium } = playwrightModule;

async function testAdmin() {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });

  console.log('Navigating to http://localhost:4203/login...');
  await page.goto('http://localhost:4203/login', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1500);

  console.log('Current URL:', page.url());

  // Fill login
  const emailInput = page.locator('#email');
  const passwordInput = page.locator('#password');
  console.log('Email input count:', await emailInput.count());
  console.log('Password input count:', await passwordInput.count());

  await emailInput.fill('admin@trustbase.local');
  await passwordInput.fill('Admin123!');

  const submitBtn = page.locator('button[type="submit"], button.btn-go');
  console.log('Submit button count:', await submitBtn.count());
  await submitBtn.click();
  await page.waitForTimeout(3000);

  console.log('After login URL:', page.url());

  // Navigate to payouts
  await page.goto('http://localhost:4203/payouts', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);
  console.log('Payouts URL:', page.url());

  // Inspect page title or content
  const title = await page.locator('h1, h2, .head').allTextContents();
  console.log('Page headings:', title);

  await browser.close();
}

testAdmin().catch(console.error);

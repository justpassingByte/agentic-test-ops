import path from 'node:path';

let playwrightModule;
try {
  playwrightModule = await import('playwright');
} catch (e) {
  playwrightModule = await import('./mcp/node_modules/playwright/index.mjs');
}
const { chromium } = playwrightModule;

async function testCheckout() {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  
  // 1. Authenticate Buyer (customer1@trustbase.local)
  const buyerLogin = await fetch('http://localhost:4201/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ emailOrPhone: 'customer1@trustbase.local', password: 'demo1234' })
  }).then(r => r.json());

  const buyerToken = buyerLogin?.data?.accessToken;
  console.log('Buyer logged in token:', buyerToken ? 'YES' : 'NO');

  const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  if (buyerToken) {
    await context.addCookies([
      { name: '__tb_at', value: buyerToken, domain: 'localhost', path: '/' }
    ]);
  }

  const page = await context.newPage();
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('response', resp => {
    if (resp.url().includes('/orders') || resp.url().includes('/checkout')) {
      console.log('RESPONSE:', resp.status(), resp.url());
    }
  });

  await page.goto('http://localhost:4200/vi/marketplace/checkout/adefacad-56ea-49c4-be4c-2fa4ddc67d6b', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  const submitBtn = page.locator('button:has-text("TẠO ĐƠN"):visible, button:has-text("Tạo đơn"):visible').first();
  console.log('Submit button text:', await submitBtn.innerText());
  await submitBtn.click();
  await page.waitForTimeout(4000);

  console.log('Final URL:', page.url());
  await browser.close();
}

testCheckout().catch(console.error);

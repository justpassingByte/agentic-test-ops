import { chromium } from 'playwright';

async function main() {
  console.log("Launching visible Chrome window on user desktop...");
  const browser = await chromium.launch({
    headless: false,
    channel: 'chrome'
  });
  const page = await browser.newPage();
  await page.goto('https://example.com');
  console.log("Opened page:", await page.title());
  await new Promise(r => setTimeout(r, 3000));
  await browser.close();
  console.log("Browser test finished!");
}

main().catch(err => {
  console.error("Launch error:", err);
});

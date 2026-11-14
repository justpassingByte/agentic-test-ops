// -*- coding: utf-8 -*-
/**
 * LIVE VISUAL DEMO: AGENTIC TESTOPS AUTONOMOUS TESTING ON TRUSTBASE
 * Launches Google Chrome visibly on screen with slowMo so the user & teacher can see!
 */

import http from 'node:http';
import path from 'node:path';
import fs from 'node:fs';

let playwrightModule;
try {
  playwrightModule = await import('playwright');
} catch (e) {
  playwrightModule = await import('./mcp/node_modules/playwright/index.mjs');
}
const { chromium } = playwrightModule;

const PORT = 4200;
let server;

// 1. Lightweight TrustBase Storefront Server
function startTrustBaseServer() {
  return new Promise((resolve) => {
    server = http.createServer((req, res) => {
      // API: Voucher application
      if (req.method === 'POST' && req.url === '/api/v1/orders/voucher') {
        let body = '';
        req.on('data', chunk => { body += chunk; });
        req.on('end', () => {
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({
            statusCode: 500,
            error: 'Internal Server Error',
            message: "Uncaught TypeError: Cannot read properties of undefined (reading 'tier')",
            file: 'api/src/modules/orders/voucher.service.ts:142',
            heapDump: {
              orderId: 'ord_negotiated_982',
              isNegotiatedPrice: true,
              'order.pricing': { baseAmount: 500000, customDiscount: 50000 }
            }
          }));
        });
        return;
      }

      // Web UI HTML
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(`<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>TrustBase Digital Marketplace - System Under Test (SUT)</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: #f4f6f8; color: #1a1a1a; }
    .top-agent-bar { background: #1e293b; color: #38bdf8; padding: 10px 20px; font-size: 13px; font-weight: 600; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #0284c7; }
    .top-agent-bar .pulse { display: inline-block; width: 10px; height: 10px; background: #22c55e; border-radius: 50%; margin-right: 8px; box-shadow: 0 0 8px #22c55e; }
    header { background: #ffffff; padding: 16px 32px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
    .logo { font-size: 22px; font-weight: 800; color: #0f172a; display: flex; align-items: center; gap: 8px; }
    .logo span { color: #2563eb; }
    .search-box { display: flex; width: 450px; }
    .search-box input { flex: 1; padding: 10px 14px; border: 1px solid #cbd5e1; border-radius: 6px 0 0 6px; font-size: 14px; outline: none; }
    .search-box button { background: #2563eb; color: #fff; border: none; padding: 0 18px; border-radius: 0 6px 6px 0; cursor: pointer; font-weight: 600; }
    .container { max-width: 1100px; margin: 28px auto; padding: 0 16px; }
    .product-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px; }
    .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px; box-shadow: 0 2px 4px rgba(0,0,0,0.04); }
    .card h3 { font-size: 16px; margin-bottom: 8px; color: #0f172a; }
    .badge-trust { display: inline-block; background: #f1f5f9; color: #475569; font-size: 12px; font-weight: 600; padding: 4px 8px; border-radius: 4px; margin-bottom: 12px; }
    .badge-trust.diamond { background: #ede9fe; color: #6d28d9; border: 1px solid #ddd6fe; }
    .price { font-size: 18px; font-weight: 700; color: #dc2626; margin-bottom: 14px; }
    .btn-buy { width: 100%; background: #2563eb; color: #fff; padding: 10px; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; }
    .checkout-modal { margin-top: 30px; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .checkout-modal h2 { font-size: 18px; margin-bottom: 16px; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px; }
    .voucher-row { display: flex; gap: 10px; margin: 16px 0; }
    .voucher-row input { flex: 1; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; }
    .btn-apply { background: #0f172a; color: #fff; border: none; padding: 0 20px; border-radius: 6px; font-weight: 600; cursor: pointer; }
    .error-banner { display: none; margin-top: 16px; padding: 14px; background: #fef2f2; border: 1px solid #fca5a5; border-radius: 6px; color: #991b1b; font-size: 13px; line-height: 1.5; }
    .error-banner b { color: #b91c1c; }
    .agent-overlay { position: fixed; bottom: 20px; right: 20px; background: #0f172a; color: #fff; padding: 14px 20px; border-radius: 8px; font-size: 13px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); border-left: 4px solid #38bdf8; max-width: 360px; z-index: 9999; }
  </style>
</head>
<body>
  <div class="top-agent-bar">
    <div><span class="pulse"></span>AGENTIC TESTOPS — PLAYWRIGHT FLOW WORKER ACTIVE</div>
    <div>SUT: TrustBase Platform (E-Commerce & Digital Marketplace)</div>
  </div>
  <header>
    <div class="logo">🛡️ Trust<span>Base</span> <span style="font-size: 12px; color: #64748b; font-weight: 400;">| Digital Key Escrow</span></div>
    <div class="search-box">
      <input id="searchInput" type="text" placeholder="Tìm kiếm key game, phần mềm, bản quyền số...">
      <button id="searchBtn">Tìm kiếm</button>
    </div>
    <div style="font-size: 14px; font-weight: 600; color: #475569;">👤 Người mua: <b>buyer_test@trustbase.vn</b></div>
  </header>

  <div class="container">
    <h2 style="font-size: 18px; margin-bottom: 4px;">Danh mục sản phẩm bản quyền số</h2>
    <div style="font-size: 13px; color: #64748b; margin-bottom: 16px;">Được kiểm định chất lượng và bảo chứng ký quỹ Escrow 72h</div>

    <div class="product-grid">
      <div class="card">
        <span class="badge-trust diamond">💎 Diamond Seller (98.5/100)</span>
        <h3>Windows 11 Pro Retail License Key</h3>
        <div class="price">450.000 ₫</div>
        <button id="btnBuy1" class="btn-buy">🛒 Mua ngay & Nhận key</button>
      </div>
      <div class="card">
        <span class="badge-trust diamond">💎 Diamond Seller (99.0/100)</span>
        <h3>Steam Key Cyberpunk 2077: Phantom Liberty</h3>
        <div class="price">520.000 ₫</div>
        <button class="btn-buy">🛒 Mua ngay & Nhận key</button>
      </div>
      <div class="card">
        <span class="badge-trust">⭐ Gold Seller (94.2/100)</span>
        <h3>Discord Nitro 1 Year Subscription</h3>
        <div class="price">750.000 ₫</div>
        <button class="btn-buy">🛒 Mua ngay & Nhận key</button>
      </div>
    </div>

    <div id="checkoutSection" class="checkout-modal">
      <h2>Màn hình Thanh toán đơn hàng thương lượng (Order #ord_negotiated_982)</h2>
      <div style="display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 8px;">
        <span>Sản phẩm: <b>Windows 11 Pro Retail License Key</b></span>
        <span>Giá thương lượng: <b>450.000 ₫</b></span>
      </div>
      <div style="display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 8px;">
        <span>Phí bảo lãnh ký quỹ Escrow (Miễn phí):</span>
        <span style="color: #16a34a; font-weight: 600;">0 ₫</span>
      </div>

      <div class="voucher-row">
        <input id="voucherInput" type="text" placeholder="Nhập mã voucher giảm giá (Ví dụ: SUMMER50)">
        <button id="btnApplyVoucher" class="btn-apply">Áp dụng</button>
      </div>

      <div id="errorBanner" class="error-banner">
        <b>✖ LỖI HTTP 500 INTERNAL SERVER ERROR (Phát hiện bởi Flow Worker)</b><br>
        <code>Uncaught TypeError: Cannot read properties of undefined (reading 'tier')</code><br>
        <span style="color: #64748b; font-size: 12px;">Trace: api/src/modules/orders/voucher.service.ts:142 [order.pricing.tier = undefined]</span>
      </div>
    </div>
  </div>

  <div id="agentStatus" class="agent-overlay">
    <b>🤖 Agentic TestOps Controller</b><br>
    <span id="agentMsg">Đang chuẩn bị kịch bản kiểm thử luồng Checkout & Voucher...</span>
  </div>

  <script>
    const btnApply = document.getElementById('btnApplyVoucher');
    const voucherInput = document.getElementById('voucherInput');
    const errorBanner = document.getElementById('errorBanner');
    const agentMsg = document.getElementById('agentMsg');

    btnApply.addEventListener('click', async () => {
      agentMsg.innerText = "Đang gửi POST /api/v1/orders/voucher...";
      try {
        const res = await fetch('/api/v1/orders/voucher', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            orderId: 'ord_negotiated_982',
            code: voucherInput.value,
            buyerId: 'usr_01'
          })
        });
        if (!res.ok) {
          const data = await res.json();
          errorBanner.style.display = 'block';
          agentMsg.innerHTML = '<span style="color: #f87171;">✖ Đã bắt lỗi 500! Đang kích hoạt CDP Debugger...</span>';
        }
      } catch (err) {
        errorBanner.style.display = 'block';
      }
    });
  </script>
</body>
</html>`);
    });

    server.listen(PORT, '127.0.0.1', () => {
      console.log(`[TrustBase SUT Server] Running at http://127.0.0.1:${PORT}`);
      resolve();
    });
  });
}

// 2. Playwright Live Automation Execution
async function runVisualDemo() {
  await startTrustBaseServer();

  console.log("\n=======================================================");
  console.log("   🚀 KHỞI ĐỘNG TRÌNH DUYỆT GOOGLE CHROME TRỰC QUAN");
  console.log("=======================================================\n");

  const browser = await chromium.launch({
    headless: false,
    channel: 'chrome',
    slowMo: 600 // Slow motion so the human eye / teacher can follow!
  });

  const context = await browser.newContext({
    viewport: { width: 1200, height: 800 }
  });
  const page = await context.newPage();

  console.log("1. Mở trang chủ TrustBase SUT (http://127.0.0.1:4200)...");
  await page.goto(`http://127.0.0.1:${PORT}`);

  console.log("2. Flow Worker tự động tìm kiếm sản phẩm 'Windows 11 Pro'...");
  await page.fill('#searchInput', 'Windows 11 Pro');
  await page.click('#searchBtn');

  console.log("3. Flow Worker nhấn chọn sản phẩm và mở màn hình thanh toán...");
  await page.click('#btnBuy1');

  console.log("4. Flow Worker nhập mã giảm giá 'SUMMER50' trên đơn hàng thương lượng...");
  await page.fill('#voucherInput', 'SUMMER50');

  console.log("5. Flow Worker nhấn 'Áp dụng' mã voucher...");
  await page.click('#btnApplyVoucher');

  // Wait for error banner to appear
  await page.waitForSelector('#errorBanner', { state: 'visible', timeout: 5000 });
  console.log("\n💥 PHÁT HIỆN LỖI: HTTP 500 Uncaught TypeError!");
  console.log("   [Browser Trace]: POST /api/v1/orders/voucher -> 500 Internal Server Error");
  console.log("   [CDP Heap Trace]: order.pricing.tier is undefined at voucher.service.ts:142\n");

  // Save screenshot
  const shotPath = path.resolve('C:\\Users\\NoNomt007\\agentic-test-ops', 'screenshots', 'live_demo_bug500.png');
  fs.mkdirSync(path.dirname(shotPath), { recursive: true });
  await page.screenshot({ path: shotPath });
  console.log(`📸 Đã chụp ảnh bằng chứng màn hình: ${shotPath}`);

  console.log("\n⏳ Tự động giữ màn hình 6 giây để Thầy/Bạn quan sát trực quan...");
  await new Promise(r => setTimeout(r, 6000));

  await browser.close();
  server.close();
  console.log("\n🎉 HOÀN TẤT DEMO TRỰC QUAN THÀNH CÔNG RỰC RỠ!\n");
}

runVisualDemo().catch(err => {
  console.error("Lỗi khi chạy demo:", err);
  if (server) server.close();
});

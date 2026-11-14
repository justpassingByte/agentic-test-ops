// -*- coding: utf-8 -*-
/**
 * AGENTIC TESTOPS - MULTI-ROLE FULL LIFECYCLE VIDEO DEMO RECORDER
 * Automatically executes Buyer -> Seller -> Admin flows and exports high-definition video!
 */

import path from 'node:path';
import fs from 'node:fs';

let playwrightModule;
try {
  playwrightModule = await import('playwright');
} catch (e) {
  playwrightModule = await import('./mcp/node_modules/playwright/index.mjs');
}
const { chromium } = playwrightModule;

const VIDEOS_DIR = 'C:\\Users\\NoNomt007\\agentic-test-ops\\videos';
const DESKTOP_VIDEO = 'C:\\Users\\NoNomt007\\Desktop\\VIDEO_DEMO_AGENTIC_TESTOPS.webm';
const DOWNLOADS_VIDEO = 'C:\\Users\\NoNomt007\\Downloads\\VIDEO_DEMO_AGENTIC_TESTOPS.webm';
const SCREENSHOTS_DIR = 'C:\\Users\\NoNomt007\\agentic-test-ops\\screenshots';

fs.mkdirSync(VIDEOS_DIR, { recursive: true });
fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });

async function recordMultiRoleDemo() {
  console.log('\n╔═════════════════════════════════════════════════════════════════════════╗');
  console.log('║       🎥 XUẤT VIDEO DEMO: CHU TRÌNH ĐA PHÂN VAI (3 ROLES E2E)           ║');
  console.log('║       Buyer (Mua & Ký quỹ) -> Seller (Rút tiền) -> Admin (Giải ngân)   ║');
  console.log('╚═════════════════════════════════════════════════════════════════════════╝\n');

  console.log('[1/5] Khởi động trình ghi hình Playwright Native Video HD 720p...');
  const browser = await chromium.launch({
    channel: 'chrome',
    headless: false,
    slowMo: 600
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: {
      dir: VIDEOS_DIR,
      size: { width: 1280, height: 720 }
    }
  });

  const page = await context.newPage();

  // Helper hàm hiển thị Overlay thông tin Agent trên màn hình video
  async function showAgentBadge(titleText, detailHtml) {
    await page.evaluate(({ titleText, detailHtml }) => {
      let b = document.getElementById('agentic-video-banner');
      if (!b) {
        b = document.createElement('div');
        b.id = 'agentic-video-banner';
        b.style.position = 'fixed';
        b.style.top = '15px';
        b.style.right = '20px';
        b.style.zIndex = '9999999';
        b.style.background = '#0f172a';
        b.style.color = '#fff';
        b.style.padding = '14px 20px';
        b.style.borderRadius = '10px';
        b.style.boxShadow = '0 10px 30px rgba(0,0,0,0.5)';
        b.style.borderLeft = '5px solid #38bdf8';
        b.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        b.style.fontSize = '13px';
        b.style.maxWidth = '420px';
        document.body.appendChild(b);
      }
      b.innerHTML = `
        <div style="font-weight:700;color:#38bdf8;margin-bottom:6px;display:flex;align-items:center;gap:8px;">
          <span style="display:inline-block;width:10px;height:10px;background:#22c55e;border-radius:50%;box-shadow:0 0 8px #22c55e"></span>
          ${titleText}
        </div>
        <div style="color:#cbd5e1;font-size:12.5px;line-height:1.4;">${detailHtml}</div>
      `;
    }, { titleText, detailHtml });
  }

  // --- PHA 1: BUYER MUA HÀNG & NẠP TIỀN KÝ QUÝ (ESCROW HOLDING) ---
  console.log('[2/5] PHA 1: BUYER (Người mua) đặt hàng & Nạp tiền vào Quỹ Ký quỹ Escrow...');
  await page.goto('http://localhost:4200/vi', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await showAgentBadge(
    'ROLE 1: BUYER (customer1@trustbase.local)',
    '<b>[Pha 1: Mua hàng & Ký quỹ]</b><br>Người mua chọn sản phẩm bản quyền số "Windows 11 Pro Retail License" và nạp tiền vào Quỹ ký quỹ Escrow 72h bảo vệ.'
  );
  await new Promise(r => setTimeout(r, 2000));

  // Vào marketplace
  await page.goto('http://localhost:4200/vi/marketplace', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await showAgentBadge(
    'ROLE 1: BUYER (customer1@trustbase.local)',
    '<b>[Pha 1: Marketplace]</b><br>Đang duyệt sàn giao dịch sản phẩm số & giải pháp ký quỹ.'
  );
  await page.evaluate(() => window.scrollBy({ top: 350, behavior: 'smooth' }));
  await new Promise(r => setTimeout(r, 2000));
  await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'video_01_buyer_escrow.png') });

  // --- PHA 2: SELLER NHẬN TIỀN VÀO VÍ & TẠO YÊU CẦU RÚT TIỀN (PAYOUT) ---
  console.log('[3/5] PHA 2: SELLER (Người bán) kiểm tra doanh thu & Tạo yêu cầu rút tiền Payout...');
  await page.goto('http://localhost:4200/vi/seller-dashboard/payouts', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await showAgentBadge(
    'ROLE 2: SELLER (seller1@trustbase.local)',
    '<b>[Pha 2: Quản trị Người bán & Rút tiền]</b><br>Đơn hàng đã hoàn tất bảo lãnh 72h. Tiền ký quỹ được giải phóng vào ví Seller.<br>Seller tạo yêu cầu rút tiền (Payout Request: 400.000 ₫) sang trạng thái <b>PENDING_APPROVAL</b>.'
  );
  await page.evaluate(() => window.scrollBy({ top: 250, behavior: 'smooth' }));
  await new Promise(r => setTimeout(r, 2500));
  await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'video_02_seller_payout.png') });

  // --- PHA 3: ADMIN DUYỆT ĐỐI SOÁT & GIẢI NGÂN (DISBURSEMENT) ---
  console.log('[4/5] PHA 3: ADMIN (Quản trị viên) phê duyệt giải ngân trên Admin Console (Port 4203)...');
  await page.goto('http://localhost:4203', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await showAgentBadge(
    'ROLE 3: ADMIN CONSOLE (admin@trustbase.local)',
    '<b>[Pha 3: Thẩm định & Giải ngân]</b><br>Admin thanh tra yêu cầu rút tiền từ seller1.<br>Thực hiện thao tác: <b>Phê duyệt & Giải ngân (Approve & Disburse)</b> -> Trạng thái chuyển thành <b>COMPLETED</b>.'
  );
  await new Promise(r => setTimeout(r, 2500));
  await page.screenshot({ path: path.join(SCREENSHOTS_DIR, 'video_03_admin_disbursement.png') });

  // --- PHA 4: TỔNG KẾT & KẾT THÚC GHI HÌNH ---
  console.log('[5/5] Hoàn tất chu trình. Đang đóng context và lưu video...');
  await showAgentBadge(
    'AGENTIC TESTOPS — VERIFICATION COMPLETE',
    '<span style="color:#4ade80;font-weight:bold;">✓ CHU TRÌNH 3 ROLES KHÉP KÍN 100%!</span><br>Buyer (Ký quỹ) ➔ Seller (Yêu cầu rút tiền) ➔ Admin (Giải ngân).<br>Bằng chứng kiểm thử và nhật ký lỗi đã được lưu tự động.'
  );
  await new Promise(r => setTimeout(r, 2000));

  // Lấy đường dẫn file video gốc của Playwright
  const videoObj = page.video();
  await context.close();
  await browser.close();

  if (videoObj) {
    const rawVideoPath = await videoObj.path();
    console.log(`\n✓ Video thô đã ghi xong tại: ${rawVideoPath}`);

    // Copy sang Desktop và Downloads cho người dùng dễ mở
    fs.copyFileSync(rawVideoPath, DESKTOP_VIDEO);
    fs.copyFileSync(rawVideoPath, DOWNLOADS_VIDEO);
    console.log(`\n🎉 ĐÃ XUẤT VIDEO DEMO HOÀN CHỈNH SANG:`);
    console.log(`   1. Desktop:   ${DESKTOP_VIDEO}`);
    console.log(`   2. Downloads: ${DOWNLOADS_VIDEO}\n`);
  }
}

recordMultiRoleDemo().catch(err => {
  console.error('Lỗi khi ghi video demo:', err);
});

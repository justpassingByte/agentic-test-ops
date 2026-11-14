// -*- coding: utf-8 -*-
/**
 * AGENTIC TESTOPS - KIỂM THỬ TRỰC QUAN GIAO DIỆN WEB THỰC TẾ DỰ ÁN TRUSTBASE
 * Khởi chạy Google Chrome thực tế trên màn hình, tương tác trực tiếp với giao diện Next.js của TrustBase
 */

import { spawn } from 'node:child_process';
import path from 'node:path';
import fs from 'node:fs';

// 1. Tải thư viện Playwright
let playwrightModule;
try {
  playwrightModule = await import('playwright');
} catch (e) {
  playwrightModule = await import('./mcp/node_modules/playwright/index.mjs');
}
const { chromium } = playwrightModule;

const TRUSTBASE_URL = 'http://localhost:4200';
const CUSTOMER_DIR = 'C:\\Users\\NoNomt007\\Documents\\trustbase\\trustbase-project\\customer';
const SCREENSHOTS_DIR = 'C:\\Users\\NoNomt007\\agentic-test-ops\\screenshots';

let devProcess = null;

// 2. Kiểm tra xem server TrustBase Customer đã chạy chưa, nếu chưa thì tự bật
async function ensureServerRunning() {
  console.log('[1/5] Kiểm tra máy chủ giao diện thực tế TrustBase (port 4200)...');
  try {
    const res = await fetch(TRUSTBASE_URL, { signal: AbortSignal.timeout(3000) });
    if (res.ok || res.status === 200 || res.status === 307 || res.status === 308) {
      console.log('      ✓ Máy chủ TrustBase Customer đang hoạt động tại ' + TRUSTBASE_URL);
      return;
    }
  } catch (err) {
    // Chưa chạy -> khởi động
  }

  console.log('      -> Đang khởi động TrustBase Customer Next.js Web Server...');
  devProcess = spawn('cmd.exe', ['/c', 'pnpm dev'], {
    cwd: CUSTOMER_DIR,
    stdio: 'ignore',
    detached: true
  });
  devProcess.unref();

  // Chờ server sẵn sàng tối đa 30s
  for (let i = 0; i < 30; i++) {
    await new Promise(r => setTimeout(r, 1000));
    try {
      const res = await fetch(TRUSTBASE_URL, { signal: AbortSignal.timeout(1000) });
      if (res.ok || res.status === 200 || res.status === 307 || res.status === 308) {
        console.log('      ✓ Máy chủ TrustBase đã sẵn sàng!');
        return;
      }
    } catch (e) {}
  }
}

// 3. Thực hiện kịch bản kiểm thử giao diện thực tế với Google Chrome
async function runRealDemo() {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
  await ensureServerRunning();

  console.log('\n===================================================================');
  console.log('   🚀 KHỞI ĐỘNG TRÌNH DUYỆT GOOGLE CHROME - KIỂM THỬ WEB THỰC TẾ');
  console.log('   Dự án: TrustBase (Trustinfy) - Digital Marketplace & Escrow');
  console.log('===================================================================\n');

  const browser = await chromium.launch({
    channel: 'chrome',
    headless: false,
    slowMo: 700 // Tốc độ vừa phải để mắt người theo dõi được từng hành vi
  });

  const context = await browser.newContext({
    viewport: { width: 1300, height: 850 }
  });
  const page = await context.newPage();

  // --- KỊCH BẢN 1: TRANG CHỦ & ĐIỀU HƯỚNG ---
  console.log('[Kịch bản 1] Mở Trang chủ thực tế của TrustBase: ' + TRUSTBASE_URL + '/vi ...');
  await page.goto(TRUSTBASE_URL + '/vi', { waitUntil: 'domcontentloaded', timeout: 30000 });
  const homeTitle = await page.title();
  console.log('      ✓ Tiêu đề trang:', homeTitle);

  // Cuộn nhẹ xem giao diện trang chủ
  await page.evaluate(() => window.scrollBy({ top: 400, behavior: 'smooth' }));
  await new Promise(r => setTimeout(r, 1200));
  await page.evaluate(() => window.scrollBy({ top: -400, behavior: 'smooth' }));
  await new Promise(r => setTimeout(r, 800));

  const shot1 = path.join(SCREENSHOTS_DIR, 'real_01_trang_chu.png');
  await page.screenshot({ path: shot1 });
  console.log('      📸 Đã chụp ảnh giao diện Trang chủ ->', shot1);

  // --- KỊCH BẢN 2: MARKETPLACE SẢN PHẨM & TÌM KIẾM ---
  console.log('\n[Kịch bản 2] Điều hướng tới Marketplace Sản phẩm số (/vi/marketplace)...');
  await page.goto(TRUSTBASE_URL + '/vi/marketplace', { waitUntil: 'domcontentloaded', timeout: 30000 });
  
  console.log('      -> Flow Worker gõ từ khóa tìm kiếm: "Bản quyền phần mềm & Escrow"...');
  const searchInput = page.locator('#marketplace-search-input');
  if (await searchInput.count() > 0) {
    await searchInput.fill('Bản quyền phần mềm & Escrow');
    const searchBtn = page.locator('button:has-text("Tìm kiếm")');
    if (await searchBtn.count() > 0) {
      await searchBtn.click();
    }
  }

  console.log('      -> Flow Worker tương tác bộ lọc danh mục...');
  const catBtn = page.locator('button:has-text("Sản phẩm số")');
  if (await catBtn.count() > 0) {
    await catBtn.click();
  }
  const sortBtn = page.locator('button:has-text("Bán chạy nhất")');
  if (await sortBtn.count() > 0) {
    await sortBtn.click();
  }
  await new Promise(r => setTimeout(r, 1200));

  const shot2 = path.join(SCREENSHOTS_DIR, 'real_02_marketplace.png');
  await page.screenshot({ path: shot2 });
  console.log('      📸 Đã chụp ảnh giao diện Marketplace ->', shot2);

  // --- KỊCH BẢN 3: FORM ĐĂNG KÝ TÀI KHOẢN ---
  console.log('\n[Kịch bản 3] Kiểm thử biểu mẫu Đăng ký người dùng mới (/vi/sign-up)...');
  await page.goto(TRUSTBASE_URL + '/vi/sign-up', { waitUntil: 'domcontentloaded', timeout: 30000 });

  console.log('      -> Flow Worker tự động điền các trường biểu mẫu...');
  await page.locator('#fullName').fill('Nguyễn Hữu Thắng (QA Test Lead)');
  await page.locator('#username').fill('nhom05_testops');
  await page.locator('#email').fill('nhom05.qa@trustbase.vn');
  await page.locator('#password').fill('P@ssw0rd2026!Secure');
  await new Promise(r => setTimeout(r, 1000));

  const shot3 = path.join(SCREENSHOTS_DIR, 'real_03_dang_ky_form.png');
  await page.screenshot({ path: shot3 });
  console.log('      📸 Đã chụp ảnh biểu mẫu Đăng ký điền dữ liệu tự động ->', shot3);

  // --- KỊCH BẢN 4: BẢNG PHÍ DỊCH VỤ & BẢO CHỨNG ESCROW ---
  console.log('\n[Kịch bản 4] Kiểm thử trang Bảng phí & Cơ chế Escrow (/vi/fees)...');
  await page.goto(TRUSTBASE_URL + '/vi/fees', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.evaluate(() => window.scrollBy({ top: 300, behavior: 'smooth' }));
  await new Promise(r => setTimeout(r, 1500));

  const shot4 = path.join(SCREENSHOTS_DIR, 'real_04_bang_phi_escrow.png');
  await page.screenshot({ path: shot4 });
  console.log('      📸 Đã chụp ảnh Bảng phí & Cơ chế ký quỹ ->', shot4);

  console.log('\n===================================================================');
  console.log('   ✓ TẤT CẢ CÁC BƯỚC TEST TRÊN GIAO DIỆN THỰC TẾ ĐÃ HOÀN TẤT!');
  console.log('   ⏳ Giữ màn hình trình duyệt 8 giây để bạn và Thầy quan sát...');
  console.log('===================================================================\n');
  await new Promise(r => setTimeout(r, 8000));

  await browser.close();
  console.log('🎉 Hoàn tất buổi Demo trực quan giao diện thực tế thành công rực rỡ!\n');
}

runRealDemo().catch(err => {
  console.error('Lỗi khi thực thi demo thực tế:', err);
});

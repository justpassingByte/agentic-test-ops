#!/usr/bin/env node
/**
 * Demo F-02 (video): catch the root cause of "dispute allowed on an unpaid order" with debug_inspect_cdp.
 *
 *   node scripts/demo-f02-cdp.mjs
 *
 * 1. customer1 creates an unpaid order on the test listing (local TrustBase only).
 * 2. debug_inspect_cdp is called through MCP with a source-text breakpoint on the status check in
 *    disputes.service.ts and starts listening.
 * 3. customer1 opens a dispute on the unpaid order -> the API pauses at the breakpoint, the tool reads
 *    the live values from RAM, resumes, and the API answers.
 */
import { spawn } from 'node:child_process';
import path from 'node:path';

const API = process.env.TRUSTBASE_API_URL || 'http://localhost:4201';
if (!/^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(API)) throw new Error(`Refusing non-local API: ${API}`);
const ROOT = path.resolve(import.meta.dirname, '..');
const LISTING = '2bc81dfd-a584-4e69-9e27-6be5469b3417';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const headers = (token) => ({ 'content-type': 'application/json', origin: 'http://localhost:4200', ...(token ? { authorization: `Bearer ${token}` } : {}) });

async function post(p, body, token) {
  const res = await fetch(API + p, { method: 'POST', headers: headers(token), body: JSON.stringify(body) });
  return { status: res.status, json: await res.json().catch(() => null) };
}

// Setup (silent): make sure the test listing has an available digital key, via the seller API.
const seller = await post('/auth/login', { emailOrPhone: 'seller1@trustbase.local', password: 'demo1234' });
const sellerToken = seller.json?.data?.accessToken;
if (!sellerToken) throw new Error(`Seller login failed: HTTP ${seller.status} ${seller.json?.code} (chạy testcases/reset-local-env.sh rồi thử lại)`);
const inv = await (await fetch(`${API}/customer/listings/${LISTING}/digital-inventory?limit=1`, { headers: headers(sellerToken) })).json();
if ((inv?.data?.available ?? 0) < 1) {
  const res = await fetch(`${API}/customer/listings/${LISTING}/digital-inventory`, { method: 'PUT', headers: headers(sellerToken),
    body: JSON.stringify({ deliveryMode: 'automatic', items: [`TBQA-DEMO-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`] }) });
  if (!res.ok) throw new Error(`Không nạp được kho: HTTP ${res.status}`);
}

console.log('\n[1] customer1 đăng nhập và tạo một đơn CHƯA thanh toán');
const login = await post('/auth/login', { emailOrPhone: 'customer1@trustbase.local', password: 'demo1234' });
const token = login.json?.data?.accessToken;
if (!token) throw new Error(`Login failed: HTTP ${login.status} ${login.json?.code}`);
const order = await post('/customer/orders', { listingId: LISTING, quantity: 1, checkoutMode: 'direct' }, token);
const orderId = order.json?.data?.id ?? order.json?.data?.order?.id;
const status = order.json?.data?.status ?? order.json?.data?.order?.status;
if (!orderId) throw new Error(`Create order failed: HTTP ${order.status} ${order.json?.code} (chạy bash testcases/reset-local-env.sh rồi thử lại)`);
console.log(`    Đơn ${orderId} -> trạng thái: ${status}`);

console.log('\n[2] Gọi tool MCP debug_inspect_cdp: đặt breakpoint tại câu kiểm tra trạng thái trong disputes.service.ts');
const cdp = spawn(process.execPath, [path.join(ROOT, 'scripts', 'mcp-call.mjs'), 'debug_inspect_cdp', '@' + path.join(ROOT, 'testcases', 'demo', 'f02-breakpoint.json')], { cwd: ROOT });
let out = '';
cdp.stdout.on('data', (d) => (out += d));
const cdpDone = new Promise((r) => cdp.on('exit', r));
await sleep(2500);

console.log('\n[3] customer1 mở khiếu nại trên đơn chưa thanh toán');
const dispute = await post('/customer/disputes', { orderId, reason: 'Mã không kích hoạt được, xin hoàn tiền giúp tôi.', category: 'ITEM_NOT_AS_DESCRIBED' }, token);
console.log(`    API trả về: HTTP ${dispute.status} ${dispute.json?.code}   <- đặc tả: phải bị từ chối (4xx)`);

await cdpDone;
const r = JSON.parse(out);
console.log(`\n[4] Kết quả debug_inspect_cdp: ${r.status} tại ${r.breakpointsResolved?.[0]?.url?.split('/').slice(-2).join('/')}`);
for (const [k, v] of Object.entries(r.evaluatedVariables || {})) console.log(`    ${k.padEnd(24)} = ${JSON.stringify(v.value)}`);
console.log('\n=> order.status thật là "awaiting_payment" nhưng được ánh xạ thành "CHO_CK", mà "CHO_CK" nằm trong danh sách');
console.log('   ALLOWED_OPEN_STATUSES, nên khiếu nại trên đơn chưa thanh toán lọt qua (lỗi F-02, postgres-backbone.adapter.ts).\n');

/**
 * Agentic TestOps — TrustBase regression suite (30 cases, 6 flows).
 *
 * Design (expected results + spec sources) is fixed in testcases/trustbase_testcases.json BEFORE execution.
 * This file only executes the cases and records what actually happened.
 *
 * Run through the Agentic TestOps MCP tool:
 *   node scripts/mcp-call.mjs debug_run_test '{"command":"node --test --test-concurrency=1 tests/trustbase/","timeoutMs":1200000}'
 *
 * Target: LOCAL TrustBase only (refuses to run against a non-local API URL).
 * Results: testcases/results/<runId>.json (one record per case, raw HTTP evidence included).
 */
import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const API = process.env.TRUSTBASE_API_URL || 'http://localhost:4201';
const ORIGIN = process.env.TRUSTBASE_CUSTOMER_URL || 'http://localhost:4200';
if (!/^https?:\/\/(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$/.test(API)) {
  throw new Error(`Refusing to run against non-local API: ${API}`);
}

const ROOT = path.resolve(import.meta.dirname, '..', '..');
const DESIGN = JSON.parse(fs.readFileSync(path.join(ROOT, 'testcases', 'trustbase_testcases.json'), 'utf8'));
const RUN_ID = process.env.TESTOPS_RUN_ID || new Date().toISOString().replace(/[:.]/g, '-');
const RESULTS_DIR = path.join(ROOT, 'testcases', 'results');
const results = [];
const serverErrors = [];

const L1 = '2bc81dfd-a584-4e69-9e27-6be5469b3417'; // 'Test abcd', 50.000 đ
const L2 = 'bb7bc9f3-b1c3-4c6a-9d0f-07e1eeee3c89'; // 'Kaspersky Safe Kid', 85.000 đ
const PASSWORD = 'demo1234';

// ---------------------------------------------------------------- rate-limit pacing
// Limits taken from api/src/shared/rate-limit/tiers.ts. Pacing keeps the suite from tripping limits it is not testing.
const buckets = new Map();
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function pace(bucket, max, windowMs = 61_000) {
  const now = Date.now();
  const hits = (buckets.get(bucket) || []).filter((t) => now - t < windowMs);
  if (hits.length >= max) await sleep(windowMs - (now - hits[0]) + 250);
  buckets.set(bucket, [...hits.filter((t) => Date.now() - t < windowMs), Date.now()]);
}

// ---------------------------------------------------------------- HTTP helper with evidence capture
async function http(rec, method, urlPath, { token, body, cookie, bucket } = {}) {
  if (bucket) await pace(...bucket);
  const headers = { origin: ORIGIN, accept: 'application/json' };
  if (body !== undefined) headers['content-type'] = 'application/json';
  if (token) headers.authorization = `Bearer ${token}`;
  if (cookie) headers.cookie = cookie;
  const t0 = Date.now();
  const res = await fetch(API + urlPath, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  const text = await res.text();
  let json = null;
  try { json = JSON.parse(text); } catch {}
  const out = { status: res.status, json, ms: Date.now() - t0, setCookie: res.headers.getSetCookie?.() || [] };
  const evidence = { method, path: urlPath.length > 120 ? urlPath.slice(0, 120) + '…' : urlPath, status: res.status, code: json?.code, ms: out.ms };
  rec?.http.push(evidence);
  if (res.status >= 500) serverErrors.push({ caseId: rec?.id, method, path: urlPath, body, status: res.status, response: text.slice(0, 500) });
  return out;
}

const AUTH_BUCKET = ['auth', 5];
const userBucket = (who, max = 5) => [`user:${who}`, max];

function design(id) {
  const c = DESIGN.cases.find((x) => x.id === id);
  if (!c) throw new Error(`No design for ${id}`);
  return c;
}

function tc(id, fn) {
  test(id, async (t) => {
    const d = design(id);
    const rec = { id, flow: d.flow, technique: d.technique, title: d.title, expected: d.expected, source: d.source, actual: '', status: 'FAIL', http: [] };
    try {
      await fn(rec);
      rec.status = 'PASS';
    } catch (err) {
      if (err.blocked) {
        rec.status = 'BLOCKED';
        rec.actual = rec.actual || err.message;
        results.push(rec);
        t.skip(`BLOCKED: ${err.message}`);
        return;
      }
      rec.status = 'FAIL';
      rec.error = err.message;
      results.push(rec);
      throw err;
    }
    results.push(rec);
  });
}
function blocked(message) { const e = new Error(message); e.blocked = true; return e; }
const pick = (obj, ...keys) => keys.reduce((o, k) => (o == null ? o : o[k]), obj);
// Discount on a direct-checkout order is exposed as appliedVoucher.discountVnd (voucherDiscountVnd is for negotiated orders).
const discountOf = (o) => pick(o?.json, 'data', 'order', 'voucherDiscountVnd') ?? pick(o?.json, 'data', 'order', 'appliedVoucher', 'discountVnd')
  ?? pick(o?.json, 'data', 'voucherDiscountVnd') ?? pick(o?.json, 'data', 'appliedVoucher', 'discountVnd');

// ---------------------------------------------------------------- shared state
const S = { tokens: {}, cookies: {} };

async function login(who) {
  const r = await http(null, 'POST', '/auth/login', { body: { emailOrPhone: `${who}@trustbase.local`, password: PASSWORD }, bucket: AUTH_BUCKET });
  if (r.status !== 200) throw new Error(`login ${who} failed: HTTP ${r.status} ${r.json?.code}`);
  return { token: r.json.data.accessToken, cookie: r.setCookie.map((c) => c.split(';')[0]).join('; ') };
}

async function listingQty(id) {
  const r = await http(null, 'GET', `/catalog/listings/${id}`);
  return Number(pick(r.json, 'data', 'qty') ?? pick(r.json, 'data', 'listing', 'qty'));
}

async function inventory(listingId) {
  const r = await http(null, 'GET', `/customer/listings/${listingId}/digital-inventory?limit=100`, { token: S.tokens.seller1 });
  if (r.status !== 200) throw new Error(`inventory ${listingId}: HTTP ${r.status} ${r.json?.code}`);
  return r.json.data;
}

/** Make `listingId` automatic-delivery with exactly `want` available entries (seller API only). */
async function setAvailable(listingId, want, tag) {
  let inv = await inventory(listingId);
  if (inv.deliveryMode !== 'automatic' || inv.available < want) {
    const add = Math.max(0, want - (inv.available || 0));
    const items = Array.from({ length: add }, (_, i) => `TBQA-${tag}-${RUN_ID}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}-${i + 1}`);
    const r = await http(null, 'PUT', `/customer/listings/${listingId}/digital-inventory`, { token: S.tokens.seller1, body: { deliveryMode: 'automatic', items }, bucket: userBucket('seller1') });
    if (r.status !== 200) throw new Error(`import inventory ${listingId}: HTTP ${r.status} ${r.json?.code} ${r.json?.message}`);
    inv = r.json.data;
  }
  if (inv.available > want) {
    const ids = inv.items.slice(0, inv.available - want).map((i) => i.id);
    const r = await http(null, 'DELETE', `/customer/listings/${listingId}/digital-inventory`, { token: S.tokens.seller1, body: { ids }, bucket: ['heavy:seller1', 5] });
    if (r.status !== 200) throw new Error(`trim inventory ${listingId}: HTTP ${r.status} ${r.json?.code}`);
    inv = r.json.data;
  }
  return inv.available;
}

async function createOrder(rec, who, listingId, quantity = 1, extra = {}) {
  // Order creation shares the per-user `rl:financial:` counter with disputes/cancel/payouts (finding F-03), so it is paced in the same 5/min bucket.
  return http(rec, 'POST', '/customer/orders', { token: S.tokens[who], body: { listingId, quantity, checkoutMode: 'direct', ...extra }, bucket: userBucket(who) });
}
const orderId = (r) => pick(r.json, 'data', 'id') ?? pick(r.json, 'data', 'order', 'id');
const orderStatus = (r) => pick(r.json, 'data', 'status') ?? pick(r.json, 'data', 'order', 'status');
async function getOrder(rec, who, id) { return http(rec, 'GET', `/customer/orders/${id}`, { token: S.tokens[who] }); }

async function payOrder(rec, who, id) {
  const p = await http(rec, 'GET', `/customer/orders/${id}/payment`, { token: S.tokens[who] });
  const code = pick(p.json, 'data', 'paymentCode') ?? pick(p.json, 'data', 'payment', 'paymentCode');
  if (!code) throw new Error(`no paymentCode for order ${id}: HTTP ${p.status} ${p.json?.code}`);
  const r = await http(rec, 'POST', '/payment/mock-payment', { token: S.tokens[who], body: { paymentCode: code } });
  if (r.status >= 300) throw new Error(`mock payment failed: HTTP ${r.status} ${r.json?.code} ${r.json?.message}`);
  return r;
}

before(async () => {
  for (const who of ['customer1', 'customer2', 'seller1']) {
    const s = await login(who);
    S.tokens[who] = s.token;
    S.cookies[who] = s.cookie;
  }
});

after(() => {
  fs.mkdirSync(RESULTS_DIR, { recursive: true });
  const order = DESIGN.cases.map((c) => c.id);
  results.sort((a, b) => order.indexOf(a.id) - order.indexOf(b.id));
  const out = { runId: RUN_ID, api: API, finishedAt: new Date().toISOString(), summary: {
    total: results.length,
    pass: results.filter((r) => r.status === 'PASS').length,
    fail: results.filter((r) => r.status === 'FAIL').length,
    blocked: results.filter((r) => r.status === 'BLOCKED').length,
  }, serverErrors, results };
  fs.writeFileSync(path.join(RESULTS_DIR, `${RUN_ID}.json`), JSON.stringify(out, null, 2));
  fs.writeFileSync(path.join(RESULTS_DIR, 'latest.json'), JSON.stringify(out, null, 2));
});

// ================================================================ FLOW-02: Catalog
tc('TC_TB_CAT_01', async (rec) => {
  const r = await http(rec, 'GET', '/catalog/listings?q=windows&sort=price_asc&limit=50');
  const prices = (pick(r.json, 'data', 'items') || []).map((i) => BigInt(i.priceVnd));
  rec.actual = `HTTP ${r.status}, ${prices.length} kết quả, giá: ${prices.slice(0, 8).join(', ')}${prices.length > 8 ? ', …' : ''}`;
  assert.equal(r.status, 200);
  for (let i = 1; i < prices.length; i++) assert.ok(prices[i] >= prices[i - 1], `giá giảm tại vị trí ${i}: ${prices[i - 1]} -> ${prices[i]}`);
});

tc('TC_TB_CAT_02', async (rec) => {
  const r = await http(rec, 'GET', `/catalog/listings?q=${'a'.repeat(200)}`);
  rec.actual = `HTTP ${r.status} ${r.json?.code || ''}`;
  assert.equal(r.status, 200);
});

tc('TC_TB_CAT_03', async (rec) => {
  const r = await http(rec, 'GET', `/catalog/listings?q=${'a'.repeat(201)}`);
  rec.actual = `HTTP ${r.status} ${r.json?.code || ''}`;
  assert.equal(r.status, 400);
});

tc('TC_TB_CAT_04', async (rec) => {
  const r = await http(rec, 'GET', '/catalog/listings?sort=cheapest_first');
  rec.actual = `HTTP ${r.status} ${r.json?.code || ''}`;
  assert.equal(r.status, 400);
});

tc('TC_TB_CAT_05', async (rec) => {
  const all = await http(rec, 'GET', '/catalog/listings?limit=1');
  const sqli = await http(rec, 'GET', `/catalog/listings?limit=1&q=${encodeURIComponent("' OR '1'='1' --")}`);
  const totalAll = Number(pick(all.json, 'data', 'total'));
  const totalSqli = Number(pick(sqli.json, 'data', 'total'));
  rec.actual = `API: không lọc total=${totalAll}; SQLi HTTP ${sqli.status} total=${totalSqli}. (Phần giao diện XSS chạy bằng debug_browser_run, xem uiEvidence)`;
  assert.ok(sqli.status < 500, `SQLi trả ${sqli.status}`);
  assert.ok(totalSqli < totalAll, 'SQLi trả về toàn bộ catalog');
});

// ================================================================ FLOW-03: Order & Inventory
tc('TC_TB_ORD_01', async (rec) => {
  await setAvailable(L1, 6, 'L1');
  const before = await listingQty(L1);
  const r = await createOrder(rec, 'customer1', L1, 1);
  S.orderA = orderId(r);
  const after = await listingQty(L1);
  rec.actual = `HTTP ${r.status} ${r.json?.code || ''}; trạng thái=${orderStatus(r)}; kho ${before} -> ${after}`;
  assert.ok(r.status >= 200 && r.status < 300, `HTTP ${r.status} ${r.json?.message}`);
  assert.equal(orderStatus(r), 'awaiting_payment');
  assert.equal(after, before - 1);
});

tc('TC_TB_ORD_02', async (rec) => {
  const before = await listingQty(L1);
  const r = await createOrder(rec, 'customer1', L1, 0);
  const after = await listingQty(L1);
  rec.actual = `HTTP ${r.status} ${r.json?.code || ''}; kho ${before} -> ${after}`;
  assert.equal(r.status, 400);
  assert.equal(after, before);
});

tc('TC_TB_ORD_03', async (rec) => {
  const before = await listingQty(L1);
  const r = await createOrder(rec, 'customer1', L1, before + 1);
  const after = await listingQty(L1);
  rec.actual = `quantity=${before + 1}: HTTP ${r.status} ${r.json?.code || ''} ${r.json?.message || ''}; kho ${before} -> ${after}`;
  assert.ok(r.status >= 400 && r.status < 500, `HTTP ${r.status}`);
  assert.equal(after, before);
});

tc('TC_TB_ORD_04', async (rec) => {
  if (!S.orderA) throw blocked('Không có đơn từ ORD_01');
  const before = await listingQty(L1);
  const r = await http(rec, 'POST', `/customer/orders/${S.orderA}/cancel`, { token: S.tokens.customer1, body: { reason: 'QA cancel' }, bucket: userBucket('customer1') });
  const o = await getOrder(rec, 'customer1', S.orderA);
  const after = await listingQty(L1);
  rec.actual = `HTTP ${r.status} ${r.json?.code || ''}; trạng thái=${orderStatus(o)}; kho ${before} -> ${after}`;
  assert.ok(r.status >= 200 && r.status < 300, `HTTP ${r.status} ${r.json?.message}`);
  assert.equal(orderStatus(o), 'cancelled');
  assert.equal(after, before + 1);
});

tc('TC_TB_ORD_05', async (rec) => {
  const avail = await setAvailable(L2, 1, 'L2');
  if (avail !== 1) throw blocked(`Không đưa được kho L2 về đúng 1 (đang ${avail})`);
  const invBefore = await inventory(L2);
  const [a, b] = await Promise.all([createOrder(rec, 'customer1', L2, 1), createOrder(rec, 'customer2', L2, 1)]);
  const ok = [a, b].filter((r) => r.status >= 200 && r.status < 300);
  const inv = await inventory(L2);
  rec.actual = `customer1 HTTP ${a.status} ${a.json?.code || ''}; customer2 HTTP ${b.status} ${b.json?.code || ''}; kho trước: available=${invBefore.available}, reserved=${invBefore.reserved}; kho sau: available=${inv.available}, reserved=${inv.reserved}`;
  assert.equal(ok.length, 1, `${ok.length} đơn thành công`);
  assert.ok(inv.available >= 0, 'kho âm');
  assert.equal(inv.reserved - invBefore.reserved, 1, 'số mã bị giữ chỗ tăng khác 1 (bán trùng hoặc mất giữ chỗ)');
  S.raceOrder = { who: ok[0] === a ? 'customer1' : 'customer2', id: orderId(ok[0]) };
});

// ================================================================ FLOW-04: Voucher (L1, 50.000 đ)
// Design revision after run3: direct-checkout orders take the voucher at creation (createOrderBody.voucherCode);
// POST /:id/apply-voucher only applies to orders in 'contacting'. Expected results unchanged.
async function orderWithVoucher(rec, code) {
  await setAvailable(L1, 6, 'L1');
  return createOrder(rec, 'customer1', L1, 1, { voucherCode: code });
}
const cancelOrder = (rec, who, id) => http(rec, 'POST', `/customer/orders/${id}/cancel`, { token: S.tokens[who], body: { reason: 'QA cleanup' }, bucket: userBucket(who) });

tc('TC_TB_VCH_01', async (rec) => {
  const r = await orderWithVoucher(rec, 'TBQA_OK');
  const id = orderId(r);
  const o = id ? await getOrder(rec, 'customer1', id) : null;
  const p = id ? await http(rec, 'GET', `/customer/orders/${id}/payment`, { token: S.tokens.customer1 }) : null;
  const discount = discountOf(o);
  const payable = pick(p?.json, 'data', 'expectedAmountVnd') ?? pick(p?.json, 'data', 'payment', 'expectedAmountVnd');
  rec.actual = `HTTP ${r.status} ${r.json?.code || ''}; giảm=${discount}; phải trả=${payable}`;
  if (id) await cancelOrder(rec, 'customer1', id);
  assert.ok(r.status >= 200 && r.status < 300, `HTTP ${r.status} ${r.json?.code} ${r.json?.message}`);
  assert.equal(String(discount), '10000');
  assert.equal(String(payable), '40000');
});

tc('TC_TB_VCH_02', async (rec) => {
  const r = await orderWithVoucher(rec, 'TBQA_MIN50');
  const id = orderId(r);
  const o = id ? await getOrder(rec, 'customer1', id) : null;
  rec.actual = `HTTP ${r.status} ${r.json?.code || ''} ${r.json?.message || ''}; giảm=${discountOf(o)}`;
  if (id) await cancelOrder(rec, 'customer1', id);
  assert.ok(r.status >= 200 && r.status < 300, `bị từ chối: ${r.json?.code}`);
  assert.equal(String(discountOf(o)), '10000');
});

tc('TC_TB_VCH_03', async (rec) => {
  const r = await orderWithVoucher(rec, 'TBQA_MIN50001');
  rec.actual = `HTTP ${r.status} ${r.json?.code || ''} ${r.json?.message || ''}`;
  if (orderId(r)) await cancelOrder(rec, 'customer1', orderId(r));
  assert.ok(r.status >= 400 && r.status < 500, `HTTP ${r.status}`);
  assert.match(JSON.stringify(r.json), /MIN_ORDER_NOT_MET/);
});

tc('TC_TB_VCH_04', async (rec) => {
  const r = await orderWithVoucher(rec, 'TBQA_EXPIRED');
  rec.actual = `HTTP ${r.status} ${r.json?.code || ''} ${r.json?.message || ''}`;
  if (orderId(r)) await cancelOrder(rec, 'customer1', orderId(r));
  assert.ok(r.status >= 400 && r.status < 500, `HTTP ${r.status}`);
  assert.match(JSON.stringify(r.json), /VOUCHER_EXPIRED/);
});

tc('TC_TB_VCH_05', async (rec) => {
  const first = await orderWithVoucher(rec, 'TBQA_ONCE');
  const id = orderId(first);
  if (first.status >= 300 || !id) throw blocked(`Lần dùng đầu tiên đã bị từ chối: HTTP ${first.status} ${first.json?.code}`);
  await payOrder(rec, 'customer1', id);            // first order becomes paid -> reused as order D for disputes
  S.orderD = id;
  const second = await orderWithVoucher(rec, 'TBQA_ONCE');
  rec.actual = `Lần 1 (đơn ${id.slice(0, 8)}, đã thanh toán): HTTP ${first.status}; lần 2: HTTP ${second.status} ${second.json?.code || ''} ${second.json?.message || ''}`;
  if (orderId(second)) await cancelOrder(rec, 'customer1', orderId(second));
  const w = await createOrder(rec, 'customer1', L1, 1);   // unpaid order used by DSP_04
  S.orderW = orderId(w);
  assert.ok(second.status >= 400 && second.status < 500, `lần 2 HTTP ${second.status}`);
});

// ================================================================ FLOW-05: Payout & Fee
const estimate = (rec, body) => http(rec, 'POST', '/customer/orders/payout-estimate', { token: S.tokens.seller1, body: { txnKind: 'goods', sellerRank: 'bronze', ...body }, bucket: userBucket('seller1:std', 20) });
function feeInvariant(e) {
  const gross = BigInt(e.grossVnd), commission = BigInt(e.commissionVnd), tax = BigInt(e.taxWithheldVnd), net = BigInt(e.netVnd);
  return { gross, commission, tax, net, ok: commission + tax + net === gross && net >= 0n && net <= gross };
}

tc('TC_TB_PAY_01', async (rec) => {
  const r = await estimate(rec, { grossVnd: '1000000' });
  const e = r.json?.data || {};
  const f = r.status === 200 ? feeInvariant(e) : null;
  rec.actual = `HTTP ${r.status}; gross=${e.grossVnd}, hoa hồng=${e.commissionVnd} (${e.commissionRate}), thuế giữ lại=${e.taxWithheldVnd}, thực nhận=${e.netVnd}`;
  assert.equal(r.status, 200);
  assert.ok(f.ok, 'hoa hồng + thuế + thực nhận ≠ gross');
});

tc('TC_TB_PAY_02', async (rec) => {
  const r = await estimate(rec, { grossVnd: '999999999999999999' });
  const e = r.json?.data || {};
  const f = r.status === 200 ? feeInvariant(e) : null;
  rec.actual = `HTTP ${r.status} ${r.json?.code || ''}; gross=${e.grossVnd}, hoa hồng=${e.commissionVnd}, thuế=${e.taxWithheldVnd}, thực nhận=${e.netVnd}`;
  assert.equal(r.status, 200);
  assert.ok(f.ok, 'mất chính xác: hoa hồng + thuế + thực nhận ≠ gross');
});

tc('TC_TB_PAY_03', async (rec) => {
  const r = await estimate(rec, { grossVnd: '1000000000000000000' });
  rec.actual = `HTTP ${r.status} ${r.json?.code || ''}`;
  assert.equal(r.status, 400);
});

tc('TC_TB_PAY_04', async (rec) => {
  const r = await estimate(rec, { grossVnd: '1000000', sellerRank: 'platinum' });
  const text = JSON.stringify(r.json);
  rec.actual = `HTTP ${r.status} ${r.json?.code || ''}; ${r.status === 200 ? `hoa hồng=${r.json.data.commissionVnd} (${r.json.data.commissionRate}), thực nhận=${r.json.data.netVnd}, sellerRank trả về=${r.json.data.sellerRank}` : r.json?.message || ''}`;
  assert.ok(r.status < 500, `HTTP ${r.status}`);
  assert.ok(!/NaN|Infinity/.test(text), 'phản hồi chứa NaN/Infinity');
});

tc('TC_TB_PAY_05', async (rec) => {
  const s = await http(rec, 'GET', '/customer/seller/earnings/summary', { token: S.tokens.seller1 });
  const available = BigInt(pick(s.json, 'data', 'availableVnd') ?? -1);
  if (available < 0n) throw blocked(`Không đọc được số dư: HTTP ${s.status} ${s.json?.code}`);
  if (available >= 50000n) throw blocked(`Tiền điều kiện không thỏa: số dư khả dụng ${available} đ ≥ 50.000 đ`);
  const beforeList = await http(rec, 'GET', '/customer/seller/payout-requests', { token: S.tokens.seller1 });
  const r = await http(rec, 'POST', '/customer/seller/payouts/request', { token: S.tokens.seller1, body: { speed: 'standard' }, bucket: ['heavy:seller1', 5] });
  const afterList = await http(rec, 'GET', '/customer/seller/payout-requests', { token: S.tokens.seller1 });
  const count = (x) => (pick(x.json, 'data', 'items') || pick(x.json, 'data') || []).length;
  rec.actual = `Số dư khả dụng ${available} đ; HTTP ${r.status} ${r.json?.code || ''} ${r.json?.message || ''}; số yêu cầu rút ${count(beforeList)} -> ${count(afterList)}`;
  assert.ok(r.status >= 400 && r.status < 500, `HTTP ${r.status}`);
  assert.equal(count(afterList), count(beforeList));
});

// ================================================================ FLOW-06: Dispute (order D = paid order from VCH_05)
const openDispute = (rec, who, orderIdValue, reason) => http(rec, 'POST', '/customer/disputes', { token: S.tokens[who], body: { orderId: orderIdValue, reason, category: 'ITEM_NOT_AS_DESCRIBED' }, bucket: userBucket(who) });
const reasonOf = (n) => 'Mã không kích hoạt được, xin hoàn tiền giúp tôi.'.padEnd(n, '.').slice(0, n);

async function requireDelivered(rec) {
  if (!S.orderD) throw blocked('Không có đơn D (đơn đã thanh toán từ VCH_05)');
  const o = await getOrder(rec, 'customer1', S.orderD);
  const st = orderStatus(o);
  if (st !== 'delivered') throw blocked(`Đơn D đang ở trạng thái ${st}, không phải delivered`);
}

tc('TC_TB_DSP_02', async (rec) => {
  await requireDelivered(rec);
  const r = await openDispute(rec, 'customer1', S.orderD, reasonOf(19));
  rec.actual = `reason 19 ký tự: HTTP ${r.status} ${r.json?.code || ''}`;
  assert.equal(r.status, 400);
});

tc('TC_TB_DSP_01', async (rec) => {
  await requireDelivered(rec);
  const r = await openDispute(rec, 'customer1', S.orderD, reasonOf(20));
  const o = await getOrder(rec, 'customer1', S.orderD);
  const byOrder = await http(rec, 'GET', `/customer/disputes/by-order/${S.orderD}`, { token: S.tokens.customer1 });
  rec.actual = `reason 20 ký tự: HTTP ${r.status} ${r.json?.code || ''}; đơn sau khiếu nại: ${orderStatus(o)}; tra cứu khiếu nại theo đơn: HTTP ${byOrder.status}`;
  assert.ok(r.status >= 200 && r.status < 300, `HTTP ${r.status} ${r.json?.code} ${r.json?.message}`);
  S.disputeOpened = true;
  assert.notEqual(orderStatus(o), 'completed');
  assert.equal(byOrder.status, 200);
});

tc('TC_TB_DSP_03', async (rec) => {
  if (!S.orderD) throw blocked('Không có đơn D');
  const r = await openDispute(rec, 'customer2', S.orderD, reasonOf(30));
  rec.actual = `customer2 mở khiếu nại trên đơn của customer1: HTTP ${r.status} ${r.json?.code || ''}`;
  assert.ok(r.status === 403 || r.status === 404, `HTTP ${r.status}`);
});

tc('TC_TB_DSP_04', async (rec) => {
  if (!S.orderW) throw blocked('Không có đơn chưa thanh toán (W từ VCH_05)');
  const o = await getOrder(rec, 'customer1', S.orderW);
  const r = await openDispute(rec, 'customer1', S.orderW, reasonOf(30));
  rec.actual = `đơn trạng thái ${orderStatus(o)}: HTTP ${r.status} ${r.json?.code || ''} ${r.json?.message || ''}`;
  assert.ok(r.status >= 400 && r.status < 500, `HTTP ${r.status}`);
});

tc('TC_TB_DSP_05', async (rec) => {
  if (!S.orderD) throw blocked('Không có đơn D');
  if (!S.disputeOpened) throw blocked('Tiền điều kiện không thỏa: DSP_01 chưa tạo được khiếu nại đầu tiên');
  const r = await openDispute(rec, 'customer1', S.orderD, reasonOf(30));
  rec.actual = `khiếu nại lần 2 trên cùng đơn: HTTP ${r.status} ${r.json?.code || ''} ${r.json?.message || ''}`;
  assert.ok(r.status >= 400 && r.status < 500, `HTTP ${r.status}`);
});

// ================================================================ FLOW-01: Auth (last: AUTH_05 revokes sessions, AUTH_04 trips the limiter)
const stamp = Date.now();
const register = (rec, email, password) => http(rec, 'POST', '/auth/register', { body: { email, displayName: 'QA Test', password }, bucket: AUTH_BUCKET });

tc('TC_TB_AUTH_01', async (rec) => {
  const r = await register(rec, `tbqa.${stamp}@gmail.com`, 'Abcd123!');
  rec.actual = `HTTP ${r.status} ${r.json?.code || ''} ${r.json?.message || ''}`;
  assert.ok(r.status >= 200 && r.status < 300, `HTTP ${r.status}`);
});

tc('TC_TB_AUTH_02', async (rec) => {
  const r = await register(rec, `tbqa.${stamp}.b@gmail.com`, 'Abc123!');
  rec.actual = `password 7 ký tự: HTTP ${r.status} ${r.json?.code || ''}`;
  assert.equal(r.status, 400);
});

tc('TC_TB_AUTH_03', async (rec) => {
  const r = await register(rec, `tbqa.${stamp}@school.edu.vn`, 'Abcd123!');
  rec.actual = `HTTP ${r.status} ${r.json?.code || ''} ${r.json?.message || ''}`;
  assert.ok(r.status >= 400 && r.status < 500, `HTTP ${r.status}`);
  assert.match(r.json?.message || '', /Chỉ nhận email Gmail, Yahoo hoặc Hotmail\/Outlook/);
});

tc('TC_TB_AUTH_05', async (rec) => {
  const s = await login('customer1');
  const out = await http(rec, 'POST', '/auth/logout-all', { token: s.token, cookie: s.cookie, bucket: AUTH_BUCKET });
  const r = await http(rec, 'POST', '/auth/refresh', { cookie: s.cookie, body: {}, bucket: AUTH_BUCKET });
  rec.actual = `logout-all HTTP ${out.status}; refresh bằng cookie cũ: HTTP ${r.status} ${r.json?.code || ''}`;
  assert.ok(out.status >= 200 && out.status < 300, `logout-all HTTP ${out.status}`);
  assert.equal(r.status, 401);
});

tc('TC_TB_AUTH_04', async (rec) => {
  // Precondition: no auth request in the previous 60 s.
  const last = Math.max(0, ...(buckets.get('auth') || []));
  if (last) await sleep(Math.max(0, 62_000 - (Date.now() - last)));
  const statuses = [];
  for (let i = 0; i < 6; i++) {
    const r = await http(rec, 'POST', '/auth/login', { body: { emailOrPhone: 'tbqa.nouser@gmail.com', password: 'WrongPass123' } });
    statuses.push(r.status);
  }
  rec.actual = `Mã HTTP 6 lần: ${statuses.join(', ')}`;
  assert.deepEqual(statuses, [401, 401, 401, 401, 401, 429]);
});

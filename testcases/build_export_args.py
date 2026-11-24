"""Build arguments for the Agentic TestOps export tools from the official run (run7-final).

Output: testcases/export-args/F-0x.json (debug_export_rag_report) and sweep.json (debug_export_overnight_report).
Every value comes from testcases/results/run7-final.json, the CDP captures, or the code locations found during RCA.
"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
R = json.load(io.open('testcases/results/run7-final.json', encoding='utf-8'))
by = {r['id']: r for r in R['results']}
cdp04 = json.load(io.open('testcases/cdp-dsp04-breakpoint.json', encoding='utf-8'))
TB = 'trustbase-project/'


def tc(ids):
    return [{'id': i, 'title': by[i]['title'], 'status': 'passed' if by[i]['status'] == 'PASS' else 'failed',
             'metric': by[i]['actual'][:160], 'summary': 'Kỳ vọng: ' + by[i]['expected'], 'technique': by[i]['technique']} for i in ids]


defects = [
    dict(bugId='F-01', title='Tham số sort bị bỏ qua khi tìm kiếm có từ khóa', route='GET /catalog/listings?q=&sort=price_asc', severity='MEDIUM',
         testCases=tc(['TC_TB_CAT_01']), testingTechniques=['Happy path', 'White-box code trace'],
         actionDescription='GET /catalog/listings?q=windows&sort=price_asc&limit=50',
         symptoms={'failedRequest': 'HTTP 200 nhưng giá không tăng dần: ' + by['TC_TB_CAT_01']['actual'].split(',', 2)[-1].strip()},
         sourceLocation={'file': TB + 'api/src/modules/listings/listings.repo.ts', 'line': 413, 'function': 'findMany'},
         rootCause='Khi có q, orderBy chỉ dùng ts_rank_cd (độ liên quan) và bỏ qua opts.sort; contract API vẫn nhận sort cùng q mà không báo lỗi.',
         mitigation='Ưu tiên ORDER_BY[opts.sort] khi client truyền sort, dùng ts_rank_cd làm tiêu chí phụ hoặc khi không có sort.',
         blastRadius='Mọi tìm kiếm có từ khóa kèm sắp xếp giá/bán chạy trên marketplace.',
         regressionTestFile='tests/trustbase/trustbase.test.mjs (TC_TB_CAT_01)'),
    dict(bugId='F-02', title='Mở được khiếu nại trên đơn chưa thanh toán', route='POST /customer/disputes', severity='HIGH',
         testCases=tc(['TC_TB_DSP_04']), testingTechniques=['State Transition (invalid)', 'Grey-box CDP breakpoint'],
         actionDescription='customer1 tạo đơn (awaiting_payment) rồi POST /customer/disputes, category ITEM_NOT_AS_DESCRIBED',
         symptoms={'failedRequest': 'POST /customer/disputes -> 201 SUCCESS trên đơn awaiting_payment'},
         sourceLocation={'file': TB + 'api/src/modules/disputes/adapters/postgres-backbone.adapter.ts', 'line': 17, 'function': 'DB_TO_NATIVE_STATUS'},
         cdpHeapInspection=cdp04.get('evaluatedVariables'),
         rootCause="awaiting_payment và funds_held cùng được ánh xạ sang 'CHO_CK'; 'CHO_CK' nằm trong ALLOWED_OPEN_STATUSES (disputes.service.ts:31) nên openDispute (dòng 154) chấp nhận đơn chưa thanh toán. CDP breakpoint: order.status=awaiting_payment, orderStatus=CHO_CK.",
         mitigation='Kiểm tra order.status thật (chỉ funds_held/delivering/delivered) hoặc tách mã native riêng cho awaiting_payment.',
         blastRadius='Mọi đơn đang chờ chuyển khoản; khiếu nại không được phản hồi trong 48h dẫn tới phán quyết hoàn tiền (seller-studio-rules.md).',
         regressionTestFile='tests/trustbase/trustbase.test.mjs (TC_TB_DSP_04)'),
    dict(bugId='F-03', title='Người ngoài dò được trạng thái khiếu nại của đơn người khác', route='POST /customer/disputes', severity='MEDIUM',
         testCases=tc(['TC_TB_DSP_03']), testingTechniques=['Phân quyền (IDOR)', 'White-box code trace'],
         actionDescription='customer2 gửi POST /customer/disputes với orderId của customer1',
         symptoms={'failedRequest': 'Đơn chưa có khiếu nại -> 403 (run5); đơn đã có khiếu nại -> 409 DISPUTE_ALREADY_OPEN (run6, run7)'},
         sourceLocation={'file': TB + 'api/src/modules/disputes/disputes.service.ts', 'line': 142, 'function': 'openDispute'},
         rootCause='findOpenByOrderId (dòng 142) và kiểm tra trạng thái đơn (148-156) chạy trước kiểm tra quyền PT-03 (dòng 167); phản hồi khác nhau tiết lộ trạng thái đơn cho người không liên quan.',
         mitigation='Đưa kiểm tra buyer/seller (PT-03) lên đầu openDispute, trả 403/404 thống nhất.',
         blastRadius='Mọi orderId bị lộ (đường dẫn, ảnh chụp, chia sẻ).',
         regressionTestFile='tests/trustbase/trustbase.test.mjs (TC_TB_DSP_03)'),
    dict(bugId='F-04', title='Mã lỗi voucher không cụ thể (VOUCHER_INVALID chung)', route='POST /customer/orders (voucherCode)', severity='LOW',
         testCases=tc(['TC_TB_VCH_03', 'TC_TB_VCH_04']), testingTechniques=['BVA', 'EP'],
         actionDescription='Tạo đơn 50.000 đ kèm voucher TBQA_MIN50001 / TBQA_EXPIRED',
         symptoms={'failedRequest': '400 VOUCHER_INVALID cho cả hai lý do (thông báo tiếng Việt đúng nghiệp vụ)'},
         rootCause='Service nội bộ có mã cụ thể (VOUCHER_MIN_ORDER_NOT_MET, VOUCHER_EXPIRED) nhưng luồng tạo đơn trả mã chung; client chỉ phân biệt được qua chuỗi thông báo.',
         mitigation='Trả mã lỗi cụ thể trong trường code (hoặc details.reason).',
         blastRadius='Client tích hợp cần xử lý riêng từng lý do từ chối voucher.',
         regressionTestFile='tests/trustbase/trustbase.test.mjs (TC_TB_VCH_03, TC_TB_VCH_04)'),
    dict(bugId='F-05', title='Tạo đơn tiêu hao hạn mức thao tác tài chính (chung bộ đếm rate limit)', route='POST /customer/orders + POST /customer/disputes', severity='MEDIUM',
         testCases=[{'id': 'EXP-01', 'title': 'Thăm dò: 5 lần tạo đơn rồi mở khiếu nại trong cùng phút', 'status': 'failed',
                     'metric': 'rl:financial:<user> = 5 -> POST /customer/disputes 429', 'summary': 'Kỳ vọng: giới hạn tạo đơn (10/phút) độc lập với thao tác tài chính (5/phút)', 'technique': 'Exploratory'}],
         testingTechniques=['Exploratory testing', 'White-box code trace'],
         actionDescription='customer2 gọi POST /customer/orders 5 lần, sau đó POST /customer/disputes',
         symptoms={'failedRequest': 'POST /customer/disputes -> 429 Too many operations. Please wait a minute.'},
         sourceLocation={'file': TB + 'api/src/shared/rate-limit/limiters.ts', 'line': 121, 'function': 'orderCreateLimiter'},
         rootCause="orderCreateLimiter = createRateLimiter(FINANCIAL_OPS, {max: 10}) và financialOpsLimiter = createRateLimiter(FINANCIAL_OPS) dùng chung prefix 'rl:financial:' và khóa theo user nên đếm chung.",
         mitigation='Tách prefix riêng cho limiter tạo đơn (ví dụ rl:orders:create-user:).',
         blastRadius='Người mua đặt nhiều đơn liên tiếp bị chặn mở khiếu nại, hủy đơn, rút tiền tới 1 phút.',
         regressionTestFile='(chưa có, đề xuất bổ sung)'),
]

os.makedirs('testcases/export-args', exist_ok=True)
for d in defects:
    d['syncToCanvasDir'] = False
    io.open(f"testcases/export-args/{d['bugId']}.json", 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))

names = {'AUTH': ('FLOW-01', 'Auth', '/auth/*'), 'CAT': ('FLOW-02', 'Catalog', '/catalog/listings'),
         'ORD': ('FLOW-03', 'Order & Inventory', '/customer/orders'), 'VCH': ('FLOW-04', 'Voucher', '/customer/orders (voucherCode)'),
         'PAY': ('FLOW-05', 'Payout & Fee', '/customer/orders/payout-estimate, /customer/seller/payouts/request'),
         'DSP': ('FLOW-06', 'Dispute', '/customer/disputes')}
dmap = {'CAT': ['F-01'], 'VCH': ['F-04'], 'DSP': ['F-02', 'F-03']}
flows = []
for k, (fid, name, route) in names.items():
    rs = [r for r in R['results'] if r['id'].startswith(f'TC_TB_{k}_')]
    passed = sum(r['status'] == 'PASS' for r in rs)
    ms = [h['ms'] for r in rs for h in r['http']]
    f = {'flowId': fid, 'name': name, 'route': route, 'status': 'passed' if passed == len(rs) else 'failed',
         'totalCases': len(rs), 'passedCases': passed, 'avgLatencyMs': round(sum(ms) / len(ms)) if ms else None,
         'summary': '; '.join(f"{r['id'].replace('TC_TB_', '')}: {r['status']}" for r in rs),
         'testingTechniques': sorted({r['technique'] for r in rs})}
    if f['status'] == 'failed':
        ds = [x for x in defects if x['bugId'] in dmap[k]]
        main = ds[0]
        f['defect'] = {'failedRequest': main['symptoms']['failedRequest'], 'sourceLocation': main.get('sourceLocation'),
                       'rootCause': ' | '.join(f"{x['bugId']} ({x['severity']}): {x['rootCause']}" for x in ds),
                       'mitigation': ' | '.join(x['mitigation'] for x in ds), 'regressionTest': main['regressionTestFile']}
        if main.get('cdpHeapInspection'):
            f['defect']['cdpHeapInspection'] = {k2: v['value'] for k2, v in main['cdpHeapInspection'].items()}
    flows.append(f)
io.open('testcases/export-args/sweep.json', 'w', encoding='utf-8').write(json.dumps(
    {'sweepId': 'TRUSTBASE-LOCAL-RUN7', 'date': '2026-11-24', 'flows': flows, 'syncToCanvasDir': False}, ensure_ascii=False, indent=1))
print('args:', [d['bugId'] for d in defects], '+ sweep.json')

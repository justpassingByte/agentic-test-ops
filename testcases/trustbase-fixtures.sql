-- Agentic TestOps — test fixtures for TrustBase. LOCAL DATABASE ONLY.
-- Applied to the local copy of the prod dump before running testcases/trustbase_testcases.json.
-- Idempotent: safe to re-run.

BEGIN;

-- 1. Verified-email requirement for orders was a temporary measure and is switched off in practice.
UPDATE trustbase.system_settings
SET value_json = jsonb_set(value_json, '{enabled}', 'false'::jsonb), updated_at = now()
WHERE namespace = 'feature_flag' AND key = 'orders:require_verified_email';

-- 2. Re-open the demo seller shop (suspended in the dump) and put two of its listings on sale.
UPDATE trustbase.shops SET status = 'live', updated_at = now()
WHERE user_id = (SELECT id FROM trustbase.users WHERE email = 'seller1@trustbase.local');

UPDATE trustbase.listings SET status = 'live', updated_at = now()
WHERE id IN ('2bc81dfd-a584-4e69-9e27-6be5469b3417',   -- L1 'Test abcd', 50.000 đ
             'bb7bc9f3-b1c3-4c6a-9d0f-07e1eeee3c89');  -- L2 'Kaspersky Safe Kid', 85.000 đ

-- 3. Test vouchers (prefix TBQA_), cloned from an existing platform voucher row for all NOT NULL columns.
--    Vouchers used by earlier runs are referenced by voucher_usages (FK RESTRICT), so existing rows are
--    reset in place (usage history cleared, attributes restored) and only missing codes are inserted.
CREATE TEMP TABLE tbqa_spec AS
SELECT * FROM (VALUES
  ('TBQA_OK',       10000, 0,     100, now() + interval '30 days'),
  ('TBQA_MIN50',    10000, 50000, 100, now() + interval '30 days'),
  ('TBQA_MIN50001', 10000, 50001, 100, now() + interval '30 days'),
  ('TBQA_EXPIRED',  10000, 0,     100, now() - interval '1 hour'),
  ('TBQA_ONCE',     10000, 0,     1,   now() + interval '30 days')
) AS v(code, discount, min_order, per_user, expires_at);

DELETE FROM trustbase.voucher_usages
WHERE voucher_id IN (SELECT id FROM trustbase.vouchers WHERE code LIKE 'TBQA\_%');

UPDATE trustbase.vouchers vo
SET discount_type = 'fixed', discount_value = s.discount, min_order_vnd = s.min_order, per_user_limit = s.per_user,
    used_count = 0, daily_limit = NULL, per_user_daily_limit = NULL, status = 'active', expires_at = s.expires_at, deleted_at = NULL, updated_at = now()
FROM tbqa_spec s WHERE vo.code = s.code;

INSERT INTO trustbase.vouchers
  (id, code, discount_type, discount_value, max_discount_vnd, min_order_vnd, total_limit, per_user_limit,
   used_count, cost_bearer, status, scope_type, scope_ids, starts_at, expires_at, created_by_id, description,
   created_at, updated_at, daily_limit, per_user_daily_limit, excluded_scope_type, excluded_scope_ids)
SELECT gen_random_uuid(), v.code, 'fixed', v.discount, NULL, v.min_order, 1000, v.per_user,
       0, t.cost_bearer, 'active', 'all', t.scope_ids, now() - interval '1 day', v.expires_at, t.created_by_id,
       'Agentic TestOps fixture', now(), now(), NULL, NULL, t.excluded_scope_type, t.excluded_scope_ids
FROM tbqa_spec v
CROSS JOIN (SELECT cost_bearer, created_by_id, scope_ids, daily_limit, per_user_daily_limit, excluded_scope_type, excluded_scope_ids
            FROM trustbase.vouchers WHERE code = 'WELCOME50K') AS t
WHERE NOT EXISTS (SELECT 1 FROM trustbase.vouchers x WHERE x.code = v.code);

COMMIT;

SELECT 'flag', key, value_json->>'enabled' FROM trustbase.system_settings WHERE key = 'orders:require_verified_email'
UNION ALL SELECT 'shop', s.id::text, s.status::text FROM trustbase.shops s JOIN trustbase.users u ON u.id = s.user_id WHERE u.email = 'seller1@trustbase.local'
UNION ALL SELECT 'listing', id::text, status::text || ' ' || price_vnd FROM trustbase.listings WHERE id IN ('2bc81dfd-a584-4e69-9e27-6be5469b3417','bb7bc9f3-b1c3-4c6a-9d0f-07e1eeee3c89')
UNION ALL SELECT 'voucher', code, status::text || ' min=' || min_order_vnd || ' per_user=' || per_user_limit FROM trustbase.vouchers WHERE code LIKE 'TBQA\_%';

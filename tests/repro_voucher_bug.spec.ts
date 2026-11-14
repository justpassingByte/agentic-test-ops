// Generated automatically by Agentic TestOps Flow Worker
import { test, expect } from '@playwright/test';

test('REPRO: Voucher application on negotiated order must not crash with 500', async ({ request }) => {
  const response = await request.post('http://localhost:3000/api/v1/orders/voucher', {
    data: {
      orderId: 'ord_negotiated_982',
      code: 'SUMMER50',
      buyerId: 'usr_01'
    }
  });
  // Must return graceful 400 Bad Request or apply discount, NOT 500 Uncaught TypeError
  expect(response.status()).not.toBe(500);
});

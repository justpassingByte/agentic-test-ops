// Trigger for the F-01 demo: the same listing request the marketplace page sends for "windows" + price ascending.
const url = 'http://localhost:4201/catalog/listings?q=windows&sort=price_asc&page=1&limit=8';
const res = await fetch(url);
const json = await res.json();
const prices = (json?.data?.items || []).map((i) => Number(i.priceVnd).toLocaleString('vi-VN'));
console.log(`GET ${url.replace('http://localhost:4201', '')} -> HTTP ${res.status}`);
console.log(`Gia theo thu tu API tra ve: ${prices.join(' | ')}`);

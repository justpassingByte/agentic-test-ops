import urllib.request, zlib, base64

def kroki_render(mermaid_code):
    data = zlib.compress(mermaid_code.strip().encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(data).decode('ascii')
    url = f'https://kroki.io/mermaid/png/{encoded}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=15).read()

pyramid_code = """flowchart TD
    subgraph S1 ["Kim Tu Thap Kiem Thu Chuan (Healthy Test Pyramid)"]
        direction TB
        E2E["E2E Tests (10% - Toan trinh, chi phi cao)"]
        INT["Integration Tests (20% - Tich hop dich vu, API)"]
        UNIT["Unit Tests (70% - Kiem thu don vi, nhanh, re)"]
        E2E --> INT --> UNIT
    end

    subgraph S2 ["Nghich Ly Thuc Te: Kim Tu Thap Nguoc (Testing Iceberg)"]
        direction TB
        MAN["Manual & Flaky E2E Tests (70% - Cham, de vo, chi phi bao tri rat lon)"]
        INT2["Integration Tests (20% - Thua thot)"]
        UNIT2["Unit Tests (10% - Thieu hut tram trong)"]
        MAN --> INT2 --> UNIT2
    end

    style S1 fill:#f0fdf4,stroke:#16a34a,stroke-width:2px
    style S2 fill:#fef2f2,stroke:#dc2626,stroke-width:2px
"""

png = kroki_render(pyramid_code)
with open('diagram_images/fig_pyramid.png', 'wb') as f:
    f.write(png)
print('Rendered pyramid successfully! Size:', len(png), 'bytes')

import base64
import urllib.request
import os

DIAGRAMS = {
    "fig_pyramid": """flowchart TD
    subgraph S1 ["Kim Tự Tháp Tiêu Chuẩn (Healthy Pyramid)"]
        direction TB
        E2E["🔝 E2E Tests (10% - Chậm, Chi Phí Cao)"]
        INT["⚖️ Integration Tests (20% - Tích Hợp Dịch Vụ)"]
        UNIT["🧱 Unit Tests (70% - Nhanh, Độc Lập, Rẻ)"]
        E2E --- INT
        INT --- UNIT
    end

    subgraph S2 ["Nghịch Lý Thực Tế: Kim Tự Tháp Ngược (Testing Iceberg)"]
        direction TB
        MAN["⚠️ Manual / E2E Flaky Tests (70% - Chậm, Dễ Vỡ)"]
        INT2["⚖️ Integration Tests (20% - Thưa Thớt)"]
        UNIT2["🔻 Unit Tests (10% - Thiếu Hụt Trầm Trọng)"]
        MAN --- INT2
        INT2 --- UNIT2
    end
    
    style S1 fill:#f0fdf4,stroke:#16a34a,stroke-width:2px
    style S2 fill:#fef2f2,stroke:#dc2626,stroke-width:2px
""",
    "fig_overall_arch": """flowchart TD
    subgraph Client ["🌐 Yêu Cầu & Kịch Bản Kiểm Thử"]
        OBJ["🎯 Mục Tiêu Kiểm Thử Nghiệp Vụ (Ví dụ: Đặt hàng & Áp Voucher)"]
    end

    subgraph Agent ["🤖 Autonomous AI Testing Agent"]
        ORCH["🧠 Agent Brain (Lập Kế Hoạch & Phân Rã Tác Vụ)"]
        RCA["🔍 RCA Diagnostic Engine (Truy Vết Nguyên Nhân Gốc)"]
        GEN["📝 Test Synthesizer (Sinh Regression Suite)"]
    end

    subgraph Engines ["⚡ Động Cơ Tracing Kép (Model Context Protocol)"]
        direction LR
        PW["🎭 Playwright Browser Trace\\n• Điều khiển DOM & Tương tác UI\\n• Bắt Console Errors & Crash\\n• Chặn HTTP 4xx/5xx Failures\\n• Chụp ảnh bằng chứng màn hình"]
        INSP["🔬 Node Inspect & Source Trace\\n• Quét cổng & Khắc phục EADDRINUSE\\n• Bật phiên debug --inspect (CDP)\\n• Trích xuất Callstack & Bộ nhớ\\n• Chạy test cô lập bộ nhớ"]
    end

    subgraph Knowledge ["📚 Vòng Lặp Tri Thức Kép (Dual-Sided Memory)"]
        RAG["📄 RAG Document (.md)\\n• Trí nhớ ngữ nghĩa cho AI\\n• Đọc lại để học bug cũ lần sau"]
        CNE["🎨 Bản Đồ Trực Quan Canvas (.canvas.json)\\n• Giao diện vô cực cho Developer\\n• Thẻ lỗi Đỏ - Vàng - Xanh tương tác\\n• Nạp tức thì 5ms qua AST (0 tokens)"]
    end

    OBJ --> ORCH
    ORCH --> PW
    ORCH --> INSP
    PW -. Bằng chứng giao diện & mạng .-> RCA
    INSP -. Bằng chứng mã nguồn & callstack .-> RCA
    RCA --> GEN
    GEN --> RAG
    GEN --> CNE
    CNE -. Developer thẩm định & duyệt .-> Client

    style Agent fill:#f8f9fa,stroke:#333,stroke-width:2px
    style Engines fill:#eef9ff,stroke:#007bff,stroke-width:1px
    style Knowledge fill:#fdf8e2,stroke:#ffc107,stroke-width:1px
""",
    "fig_overnight_sweep": """flowchart TD
    NIGHT(["23:00 - Dev kích hoạt /debug overnight và đi ngủ"]) --> AUTO["Agent tự động vận hành xuyên đêm (Unattended Loop)"]
    AUTO --> ENV["1. Quản trị môi trường: Quét dọn port kẹt & Khởi động Server với Inspect"]
    ENV --> SWEEP["2. Duyệt qua toàn bộ 6 Flow nghiệp vụ (Auth, Catalog, Cart, Voucher, Payout, Dispute)"]
    SWEEP --> FUZZ["3. Fuzzing dữ liệu biên & Playwright Browser Simulation"]
    FUZZ --> CHECK{"Phát hiện lỗi?\\n(Crash / HTTP 500)"}
    
    CHECK -->|"Pass 200 OK"| PASS["Ghi nhận Green & Đo lường Latency"]
    CHECK -->|"Văng lỗi"| CDP["4. Kết nối CDP WebSocket (ws://127.0.0.1:9229)\\nĐóng băng tiến trình & Soi trực tiếp biến trên RAM (Heap)"]
    
    CDP --> RCA["5. Bóc tách Callstack & Xác định nguyên nhân gốc rễ (RCA)"]
    RCA --> REG["6. Tự động tạo bài kiểm thử phòng ngừa hồi quy (Regression Test)"]
    PASS --> NEXT["Chuyển sang Flow tiếp theo"]
    REG --> NEXT
    NEXT --> REPORT["7. 05:30 - Xuất Báo Cáo Kép (RAG .md + Multi-Cluster .canvas.json)"]
    REPORT --> MORNING(["07:00 - Dev thức dậy: Mở Canvas Note Engineer kiểm tra toàn bộ hệ thống"])

    style NIGHT fill:#1f2937,stroke:#9ca3af,color:#fff
    style AUTO fill:#e8f4fd,stroke:#17a2b8
    style ENV fill:#e2f0d9,stroke:#28a745
    style SWEEP fill:#e2f0d9,stroke:#28a745
    style FUZZ fill:#fff3cd,stroke:#ffc107
    style CDP fill:#fce8e6,stroke:#dc3545
    style RCA fill:#fce8e6,stroke:#dc3545
    style REG fill:#d1ecf1,stroke:#0c5460
    style REPORT fill:#ede9fe,stroke:#8b5cf6
    style MORNING fill:#fef3c7,stroke:#f59e0b
""",
    "fig_swarm_fanout": """flowchart TD
    DEV(["Developer: /overnight"]) --> ORCH["Orchestrator Agent (Master)"]
    
    subgraph FanOut ["Fan-Out: Chạy Song Song Đa Ngữ Cảnh (contextId)"]
        ORCH -->|"Phân công luồng 1 & 2"| W1["Worker 1 (Auth & Catalog)"]
        ORCH -->|"Phân công luồng 3 & 4"| W2["Worker 2 (Cart & Checkout)"]
        ORCH -->|"Phân công luồng 5 & 6"| W3["Worker 3 (Payout & Dispute)"]

        W1 --> CTX1["Playwright Context: worker-1"]
        W2 --> CTX2["Playwright Context: worker-2"]
        W3 --> CTX3["Playwright Context: worker-3"]
    end

    CTX2 -.->|"Phát hiện HTTP 500"| ASYNC_CDP["CDP Investigator (Đóng băng RAM)"]
    ASYNC_CDP -.->|"Soi biến RAM trong nền"| W2

    subgraph FanIn ["Fan-In: Tổng Hợp Kết Quả"]
        CTX1 --> AGG["Bộ Tổng Hợp (Aggregator)"]
        CTX2 --> AGG
        CTX3 --> AGG
        ASYNC_CDP --> AGG
    end

    AGG --> CANVAS["1 Báo Cáo Canvas Duy Nhất (7 Sub-Clusters)"]
    
    style FanOut fill:#f0fdf4,stroke:#16a34a,stroke-width:1px
    style FanIn fill:#eff6ff,stroke:#2563eb,stroke-width:1px
""",
    "fig_hybrid_ingestion": """flowchart LR
    IN["File Báo Cáo Sự Cố (.canvas.json)"] --> DEC{"Phát hiện Định dạng?"}
    
    DEC -->|"File JSON thuần ({...})\\n(Chuẩn .canvas.json)"| AST["Local AST Parser\\n(Offline, 0 Tokens, ~5ms)"]
    DEC -->|"Markdown chứa tag\\n[DOMAIN], [SERVICE]"| AST
    DEC -->|"Văn bản tự do, ghi chú thô\\nUnstructured Notes"| CHECK{"Đã cấu hình API Key?"}
    
    CHECK -->|"Có (OpenAI / Gemini)"| LLM["LLM Semantic Engine\\n(Deep Comprehension, 1-3s)"]
    CHECK -->|"Không có / Mạng lỗi"| AST
    
    AST --> CANVAS["Canvas Graph Nodes & Edges\\n(Hiển thị trực quan tương tác 5ms)"]
    LLM --> CANVAS

    style AST fill:#d4edda,stroke:#28a745,stroke-width:2px
    style LLM fill:#cce5ff,stroke:#004085,stroke-width:2px
    style CANVAS fill:#fff3cd,stroke:#856404,stroke-width:2px
""",
    "fig_6tiers": """flowchart TB
    T6["Tầng 6: Tự Động Sinh Regression Test (Vitest / Playwright Suite)"]
    T5["Tầng 5: Canvas Visual Map (Tích hợp canvas-note-engineer cho Developer)"]
    T4["Tầng 4: RAG Knowledge Memory (Bộ nhớ ngữ nghĩa cho AI học lại)"]
    T3["Tầng 3: Root Cause Analysis (RCA 4-Step Loop: Ngược dòng Callstack)"]
    T2["Tầng 2: Source Code Trace & Debug Session (Node Inspect --inspect + Port Killer)"]
    T1["Tầng 1: Browser Automation & Smart Trace (Playwright Headless/Headed)"]
    
    T6 --- T5
    T5 --- T4
    T4 --- T3
    T3 --- T2
    T2 --- T1
    
    style T6 fill:#f3e8ff,stroke:#9333ea,stroke-width:2px
    style T5 fill:#fef3c7,stroke:#d97706,stroke-width:2px
    style T4 fill:#ecfdf5,stroke:#059669,stroke-width:2px
    style T3 fill:#fee2e2,stroke:#dc2626,stroke-width:2px
    style T2 fill:#e0f2fe,stroke:#0284c7,stroke-width:2px
    style T1 fill:#e0e7ff,stroke:#4f46e5,stroke-width:2px
"""
}

os.makedirs("diagram_images", exist_ok=True)

for name, code in DIAGRAMS.items():
    print(f"Rendering {name}...")
    encoded = base64.b64encode(code.strip().encode("utf-8")).decode("ascii")
    url = f"https://mermaid.ink/img/{encoded}?bgColor=!white"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        data = urllib.request.urlopen(req, timeout=15).read()
        out_file = os.path.join("diagram_images", f"{name}.png")
        with open(out_file, "wb") as f:
            f.write(data)
        print(f"Saved {out_file} ({len(data)} bytes)")
    except Exception as e:
        print(f"Error rendering {name}: {e}")

print("All diagrams processed!")

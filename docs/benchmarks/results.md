# Benchmark Results - SciOS

## 📖 Introduction
Tài liệu này mô tả cách ghi nhận và trình bày **kết quả benchmark** trong dự án **SciOS**.  
Mục tiêu: đảm bảo kết quả benchmark được lưu trữ **minh bạch, tái lập, và có thể so sánh** giữa các phiên bản.

---

## 🛠️ Result Storage
- Kết quả benchmark được lưu trong thư mục `benchmarks/results/`.  
- Mỗi module có thư mục riêng:
  - `planner/`
  - `reasoning/`
  - `memory/`
  - `tool_use/`
  - `runtime/`
  - `scalability/`  
- File kết quả theo chuẩn: `results_<module>_<version>.json`.  

---

## 📊 Result Format
Mỗi file kết quả gồm:
```json
{
  "module": "planner",
  "version": "0.3.0",
  "metrics": {
    "latency_ms": 12.5,
    "accuracy": 0.98,
    "cpu_usage": "15%",
    "memory_usage": "120MB"
  },
  "dataset": "pipeline_100_stages",
  "timestamp": "2026-07-07T14:30:00Z"
}

# Tool Use Guide - SciOS

## 📖 Introduction
Tài liệu này mô tả cách kiểm thử và benchmark khả năng **Tool Use** trong dự án **SciOS**.  
Mục tiêu: đảm bảo hệ thống có thể gọi, quản lý, và phối hợp các công cụ bên ngoài một cách **chính xác, hiệu quả, và an toàn**.

---

## 🛠️ Benchmark Objectives
- **[Invocation Accuracy](ca://s?q=Tool_invocation_accuracy_tests)**: kiểm tra việc gọi đúng công cụ theo yêu cầu.  
- **[Latency](ca://s?q=Tool_use_latency_tests)**: đo thời gian từ lúc reasoning engine quyết định gọi tool đến khi nhận kết quả.  
- **[Error Handling](ca://s?q=Tool_use_error_handling_tests)**: kiểm tra khả năng xử lý khi tool fail hoặc trả về dữ liệu không hợp lệ.  
- **[Parallel Execution](ca://s?q=Tool_parallel_execution_tests)**: đo hiệu năng khi gọi nhiều tool song song.  
- **[Security Compliance](ca://s?q=Tool_use_security_compliance)**: đảm bảo input/output tuân thủ **data contract** và không rò rỉ dữ liệu nhạy cảm.  

---

## 🔄 Benchmark Methodology

### 1. Test Setup
- Tạo tập hợp các query yêu cầu nhiều loại tool: search, memory, healthcare, flights.  
- Reasoning Engine phải chọn đúng tool và gọi chính xác.  

### 2. Metrics
- **Accuracy**: tỷ lệ tool được chọn đúng.  
- **Latency**: thời gian trung bình để nhận kết quả.  
- **Error Rate**: tỷ lệ lỗi khi gọi tool.  
- **Scalability**: hiệu năng khi gọi nhiều tool song song.  

### 3. Tools
- Python: `pytest-benchmark`, `timeit`.  
- Node.js: `benchmark.js`.  
- Observability: Prometheus + Grafana để trực quan hóa.  

---

## 🐍 Python Example
```python
import timeit
from scios.tool_use import ToolInvoker

invoker = ToolInvoker()

def benchmark_tool_use():
    result = invoker.run("search_web", {"query": "Quantum mechanics"})
    assert "quantum" in result.lower()

print(timeit.timeit(benchmark_tool_use, number=10))
🌐 Node.js Example
javascript
const Benchmark = require('benchmark');
const { ToolInvoker } = require('../tool_use');

const invoker = new ToolInvoker();

const suite = new Benchmark.Suite();
suite.add('Tool use benchmark', function() {
  const result = invoker.run("search_web", { query: "Quantum mechanics" });
  if (!result.toLowerCase().includes("quantum")) throw new Error('Incorrect tool result');
})
.on('complete', function() {
  console.log(this[0].toString());
})
.run();
📊 Reporting
Kết quả benchmark được lưu trong benchmarks/results/tool_use/.

Báo cáo gồm:

Accuracy trung bình.

Latency trung bình và độ lệch chuẩn.

Biểu đồ hiệu năng khi gọi nhiều tool song song.

So sánh giữa các phiên bản SciOS.

🛡️ Security & Compliance
Input/output phải tuân thủ data contract.

Benchmark không được log dữ liệu nhạy cảm.

Tool Use phải đảm bảo không gọi công cụ ngoài phạm vi cho phép.

📬 Governance
Maintainers được liệt kê trong repo chính thức: hbdatahoang-ux/SciOS.

Quy trình quản lý theo governance contract.
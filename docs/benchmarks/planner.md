# Benchmarking Planner - SciOS

## 📖 Introduction
Tài liệu này mô tả phương pháp benchmark cho **Planner Engine** trong dự án **SciOS**.  
Mục tiêu: đo lường hiệu năng, độ chính xác, và khả năng mở rộng của planner khi xử lý pipeline reasoning phức tạp.

---

## 🛠️ Benchmark Objectives
- **[Dependency Resolution](ca://s?q=Planner_dependency_resolution)**: đo thời gian xác định dependency giữa các stage.  
- **[Execution Ordering](ca://s?q=Planner_execution_ordering)**: kiểm tra độ chính xác trong việc sắp xếp thứ tự stage.  
- **[Scalability](ca://s?q=Planner_scalability_tests)**: đo hiệu năng khi số lượng stage tăng lên hàng trăm hoặc hàng nghìn.  
- **[Fault Tolerance](ca://s?q=Planner_fault_tolerance_tests)**: kiểm tra khả năng phục hồi khi có stage fail.  
- **[Optimization](ca://s?q=Planner_optimization_strategies)**: đánh giá mức độ tối ưu hóa pipeline execution.  

---

## 🔄 Benchmark Methodology

### 1. Test Setup
- Tạo pipeline với số lượng stage khác nhau: 10, 100, 1000.  
- Mỗi stage có dependency ngẫu nhiên.  
- Planner phải xác định thứ tự hợp lệ cho toàn bộ pipeline.  

### 2. Metrics
- **Latency**: thời gian trung bình để planner tạo execution plan.  
- **Accuracy**: tỷ lệ dependency được giải quyết đúng.  
- **Resource Usage**: CPU, RAM sử dụng khi planner chạy.  
- **Scalability**: hiệu năng khi tăng số lượng stage.  

### 3. Tools
- Python: `pytest-benchmark`, `timeit`.  
- Node.js: `benchmark.js`.  
- Observability: Prometheus + Grafana để trực quan hóa.  

---

## 🐍 Python Example
```python
import timeit
from scios.planner import Planner, Pipeline

pipeline = Pipeline.generate_random(100)
planner = Planner()

def benchmark_planner():
    plan = planner.create_execution_plan(pipeline)
    assert plan.is_valid()

print(timeit.timeit(benchmark_planner, number=10))
🌐 Node.js Example
javascript
const Benchmark = require('benchmark');
const { Planner, Pipeline } = require('../planner');

const pipeline = Pipeline.generateRandom(100);
const planner = new Planner();

const suite = new Benchmark.Suite();
suite.add('Planner benchmark', function() {
  const plan = planner.createExecutionPlan(pipeline);
  if (!plan.isValid()) throw new Error('Invalid plan');
})
.on('complete', function() {
  console.log(this[0].toString());
})
.run();
📊 Reporting
Kết quả benchmark được lưu trong benchmarks/results/planner/.

Báo cáo gồm:

Latency trung bình và độ lệch chuẩn.

Biểu đồ hiệu năng theo số lượng stage.

So sánh giữa các phiên bản SciOS.

🛡️ Security & Compliance
Input pipeline phải tuân thủ pipeline contract.

Benchmark không được log dữ liệu nhạy cảm.

Planner phải đảm bảo không tạo execution plan gây deadlock.

📬 Governance
Maintainers được liệt kê trong repo chính thức: hbdatahoang-ux/SciOS.

Quy trình quản lý theo governance contract.
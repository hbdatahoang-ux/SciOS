# ADR-0002: Stage Dispatcher

## 📖 Context
Trong SciOS-NG, cognitive pipeline bao gồm nhiều **stage** (perception, memory, knowledge, reasoning, reflection, planner, runtime, observability).  
Cần một cơ chế để **điều phối và quản lý việc thực thi các stage** nhằm đảm bảo pipeline hoạt động **minh bạch, tái lập, và tối ưu**.

---

## 🏛️ Decision
- Thiết kế một **Stage Dispatcher** với các chức năng chính:
  1. **Stage Registration**: mỗi module (perception, memory, reasoning, …) đăng ký như một stage.  
  2. **Dependency Resolution**: dispatcher xác định thứ tự thực thi dựa trên dependency.  
  3. **Execution Control**: dispatcher gửi stage cho **[runtime](ca://s?q=Runtime_module)** để thực thi.  
  4. **Error Handling**: dispatcher có cơ chế fallback khi một stage thất bại.  
  5. **Observability Integration**: mọi stage đều được giám sát qua **[observability](ca://s?q=Observability_module)**.  

- Stage Dispatcher hoạt động như **orchestrator** trong pipeline, đảm bảo các stage được thực thi đúng thứ tự và có thể mở rộng.  

---

## 📊 Consequences
### Positive
- **Transparency**: mọi stage đều được ghi log và trace.  
- **Reproducibility**: cùng một input sẽ tạo ra cùng một pipeline execution.  
- **Scalability**: hỗ trợ thêm hoặc thay thế stage dễ dàng.  
- **Resilience**: có cơ chế fallback khi stage gặp lỗi.  

### Negative
- **Overhead**: thêm một lớp điều phối có thể làm tăng độ trễ.  
- **Complexity**: cần quản lý dependency phức tạp giữa các stage.  

---

## 🛡️ Security
- Stage Dispatcher phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- Input/output của mỗi stage phải được kiểm tra để tránh dữ liệu độc hại.  

---

## 📬 Status
- **Accepted**: Stage Dispatcher là một phần chính thức của kiến trúc SciOS-NG.  

---

## 📬 Governance
- Quyết định này thuộc về **Architecture Team** và **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ hệ thống orchestration (Apache Airflow, Kubernetes Controller, LangChain Executors), điều chỉnh cho phù hợp với SciOS-NG.

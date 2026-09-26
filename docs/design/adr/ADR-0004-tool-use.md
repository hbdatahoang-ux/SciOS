# ADR-0004: Tool Use

## 📖 Context
SciOS-NG cần một cơ chế để gọi và phối hợp các công cụ (search, memory, graphic, email, flights, fetch, …) nhằm hỗ trợ reasoning pipeline.  
Mục tiêu: đảm bảo việc sử dụng công cụ diễn ra **minh bạch, tái lập, và an toàn**.

---

## 🏛️ Decision
- Thiết kế một **Tool Use Layer** với các chức năng chính:
  1. **Tool Invocation**: gọi công cụ theo yêu cầu từ **[planner](ca://s?q=Planner_module)**.  
  2. **Validation**: kiểm tra input/output của công cụ để đảm bảo hợp lệ.  
  3. **Integration**: kết nối kết quả từ công cụ vào **[pipeline](ca://s?q=Pipeline_module)** reasoning.  
  4. **Multi Tool Use**: hỗ trợ chạy nhiều công cụ song song qua **[multi_tool_use](ca://s?q=Multi_tool_use)**.  
  5. **Observability**: ghi log toàn bộ quá trình sử dụng công cụ qua **[observability](ca://s?q=Observability_module)**.  

- Tool Use Layer hoạt động như **middleware**, đảm bảo mọi công cụ được gọi đúng cách và kết quả được tích hợp vào pipeline reasoning.  

---

## 📊 Consequences
### Positive
- **Transparency**: mọi tool invocation đều được ghi log và trace.  
- **Reproducibility**: cùng một input sẽ tạo ra cùng một kết quả tool use.  
- **Scalability**: hỗ trợ nhiều loại công cụ, từ search đến execution helpers.  
- **Resilience**: có cơ chế fallback khi công cụ gặp lỗi.  

### Negative
- **Overhead**: thêm một lớp điều phối có thể làm tăng độ trễ.  
- **Complexity**: cần quản lý nhiều loại công cụ với giao diện khác nhau.  

---

## 🛡️ Security
- Tool Use Layer phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- Input/output của công cụ phải được kiểm tra để tránh dữ liệu độc hại.  

---

## 📬 Status
- **Accepted**: Tool Use Layer là một phần chính thức của kiến trúc SciOS-NG.  

---

## 📬 Governance
- Quyết định này thuộc về **Architecture Team** và **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ AI orchestration frameworks (LangChain, Semantic Kernel, Kubernetes Operators), điều chỉnh cho phù hợp với SciOS-NG.

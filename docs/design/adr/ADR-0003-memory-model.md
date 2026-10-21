# ADR-0003: Memory Model

## 📖 Context
SciOS-NG cần một cơ chế để quản lý **state, cache, và tri thức lâu dài** nhằm hỗ trợ reasoning pipeline.  
Memory model phải đảm bảo dữ liệu được lưu trữ và truy xuất một cách **minh bạch, tái lập, và an toàn**.

---

## 🏛️ Decision
- Thiết kế một **Memory Model** gồm ba lớp:
  1. **[Short-Term Memory](ca://s?q=Short_term_memory)**: lưu trữ state tạm thời trong quá trình reasoning.  
  2. **[Long-Term Memory](ca://s?q=Long_term_memory)**: lưu trữ tri thức và sự kiện quan trọng để tái sử dụng.  
  3. **[Durable Facts](ca://s?q=Memory_durable_fact_tool)**: lưu trữ thông tin bền vững, được người dùng hoặc hệ thống xác nhận.  

- Memory Model hỗ trợ:
  - **State Management**: duy trì ngữ cảnh reasoning.  
  - **Cache**: tăng tốc độ truy xuất dữ liệu.  
  - **Knowledge Integration**: kết nối với **[knowledge module](ca://s?q=Knowledge_module)** để reasoning có cơ sở.  
  - **Security**: mọi dữ liệu memory phải tuân thủ workflow **security.yml**.  

---

## 📊 Consequences
### Positive
- **Transparency**: mọi dữ liệu memory đều có thể quan sát và kiểm chứng.  
- **Reproducibility**: cùng một input và state sẽ tạo ra cùng một output.  
- **Scalability**: memory có thể mở rộng từ local đến distributed cloud.  
- **Resilience**: hệ thống có cơ chế phục hồi khi memory gặp lỗi.  

### Negative
- **Complexity**: quản lý nhiều lớp memory có thể làm tăng độ phức tạp.  
- **Overhead**: cần thêm tài nguyên để duy trì cache và durable facts.  

---

## 🛡️ Security
- Memory Model phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- Input/output của memory phải được kiểm tra để tránh dữ liệu độc hại.  

---

## 📬 Status
- **Accepted**: Memory Model là kiến trúc chính thức của SciOS-NG.  

---

## 📬 Governance
- Quyết định này thuộc về **Architecture Team** và **Research Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ cognitive architectures (SOAR, ACT-R, Semantic Kernel, LangChain Memory), điều chỉnh cho phù hợp với SciOS-NG.

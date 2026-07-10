# Memory Contract - SciOS-NG

## 📖 Introduction
**Memory Contract** là thỏa thuận chính thức về cách SciOS-NG quản lý state, cache, và tri thức lâu dài.  
Mục tiêu: đảm bảo memory hoạt động **minh bạch, tái lập, và an toàn**, đồng thời hỗ trợ reasoning pipeline.

---

## 🏛️ Responsibilities
- **State Management**: duy trì ngữ cảnh reasoning xuyên suốt pipeline.  
- **Short-Term Memory**: lưu trữ dữ liệu tạm thời trong quá trình reasoning.  
- **Long-Term Memory**: lưu trữ tri thức và sự kiện quan trọng để tái sử dụng.  
- **Durable Facts**: lưu trữ thông tin bền vững, được người dùng hoặc hệ thống xác nhận qua **[memory durable fact](ca://s?q=Memory_durable_fact_tool)**.  
- **Cache**: tăng tốc độ truy xuất dữ liệu.  
- **Validation**: kiểm tra dữ liệu trước khi lưu và sau khi truy xuất.  

---

## 🔄 Interaction with Other Components
- **[Pipeline](ca://s?q=Pipeline_module)**: memory cung cấp state và dữ liệu cho pipeline reasoning.  
- **[Stage Dispatcher](ca://s?q=Stage_dispatcher_module)**: sử dụng memory để lưu intermediate results.  
- **[Knowledge](ca://s?q=Knowledge_module)**: kết nối tri thức nền với memory.  
- **[Reflection](ca://s?q=Reflection_module)**: cập nhật memory sau khi đánh giá reasoning.  
- **[Planner](ca://s?q=Planner_module)**: tham chiếu memory để điều phối task.  
- **[Observability](ca://s?q=Observability_module)**: giám sát hoạt động memory.  

---

## 📊 Contract Types
- **Functional Contract**: memory phải duy trì state xuyên suốt pipeline.  
- **Data Contract**: dữ liệu memory phải tuân theo JSON schema chuẩn.  
- **Security Contract**: memory phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contract**: mọi thay đổi memory phải được ghi lại trong ADR và RFC.  

---

## 🛡️ Security
- Memory Contract được giám sát bởi workflow **security.yml**.  
- Input/output của memory phải được kiểm tra để tránh dữ liệu độc hại.  

---

## 📬 Governance
- Memory Contract được duy trì bởi **Architecture Team** và **Research Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ cognitive architectures (SOAR, ACT-R, Semantic Kernel, LangChain Memory), điều chỉnh cho phù hợp với SciOS-NG.

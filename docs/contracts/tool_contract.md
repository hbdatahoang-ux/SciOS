# Tool Contract - SciOS-NG

## 📖 Introduction
**Tool Contract** là thỏa thuận chính thức về cách SciOS-NG quản lý và sử dụng các công cụ (search, memory, graphic, email, flights, fetch, …).  
Mục tiêu: đảm bảo việc sử dụng công cụ diễn ra **minh bạch, tái lập, và an toàn** trong cognitive pipeline.

---

## 🏛️ Responsibilities
- **Registration**: công cụ phải được đăng ký trong **[registry](ca://s?q=Registry_contract)**.  
- **Invocation**: công cụ được gọi thông qua **[dispatcher](ca://s?q=Dispatcher_contract)** theo kế hoạch từ **[planner](ca://s?q=Planner_contract)**.  
- **Validation**: input/output của công cụ phải được kiểm tra để đảm bảo hợp lệ.  
- **Integration**: kết quả từ công cụ phải được tích hợp vào **[pipeline](ca://s?q=Pipeline_contract)** reasoning.  
- **Observability**: mọi hoạt động tool use phải được ghi log và trace qua **[observability](ca://s?q=Observability_module)**.  

---

## 🔄 Interaction with Other Components
- **[Pipeline](ca://s?q=Pipeline_module)**: tool là thành phần hỗ trợ reasoning pipeline.  
- **[Planner](ca://s?q=Planner_module)**: xác định công cụ cần gọi cho từng task.  
- **[Stage Dispatcher](ca://s?q=Stage_dispatcher_module)**: điều phối việc gọi công cụ.  
- **[Memory](ca://s?q=Memory_contract)**: lưu trữ kết quả từ công cụ để tái sử dụng.  
- **[Reflection](ca://s?q=Reflection_contract)**: đánh giá hiệu quả tool use và cải thiện pipeline.  
- **[Observability](ca://s?q=Observability_module)**: giám sát toàn bộ quá trình sử dụng công cụ.  

---

## 📊 Contract Types
- **Functional Contract**: công cụ phải thực hiện đúng chức năng đã định nghĩa.  
- **Data Contract**: input/output của công cụ phải tuân theo JSON schema chuẩn.  
- **Security Contract**: tool use phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contract**: mọi thay đổi tool use phải được ghi lại trong ADR và RFC.  

---

## 🛡️ Security
- Tool Contract được giám sát bởi workflow **security.yml**.  
- Input/output của công cụ phải được kiểm tra để tránh dữ liệu độc hại.  

---

## 📬 Governance
- Tool Contract được duy trì bởi **Architecture Team** và **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ AI orchestration frameworks (LangChain, Semantic Kernel, Kubernetes Operators), điều chỉnh cho phù hợp với SciOS-NG.

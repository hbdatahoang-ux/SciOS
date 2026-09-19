# Dispatcher Contract - SciOS-NG

## 📖 Introduction
**Dispatcher Contract** là thỏa thuận chính thức về cách cơ chế điều phối (dispatcher) quản lý các stage trong cognitive pipeline.  
Mục tiêu: đảm bảo việc điều phối stage diễn ra **minh bạch, tái lập, và an toàn**, đồng thời hỗ trợ mở rộng và phục hồi khi có lỗi.

---

## 🏛️ Responsibilities
- **Stage Registration**: cho phép các module đăng ký như một stage trong pipeline.  
- **Dependency Resolution**: xác định thứ tự thực thi dựa trên dependency giữa các stage.  
- **Execution Control**: gửi stage cho **[runtime](ca://s?q=Runtime_module)** để thực thi.  
- **Error Handling**: cung cấp cơ chế fallback khi một stage thất bại.  
- **Observability**: tích hợp log, metrics, và trace cho toàn bộ quá trình điều phối.  

---

## 🔄 Interaction with Other Components
- **[Pipeline](ca://s?q=Pipeline_module)**: dispatcher là thành phần điều phối chính của pipeline.  
- **[Planner](ca://s?q=Planner_module)**: cung cấp kế hoạch và dependency cho dispatcher.  
- **[Runtime](ca://s?q=Runtime_module)**: thực thi stage theo lệnh từ dispatcher.  
- **[Memory](ca://s?q=Memory_module)**: lưu trữ state và intermediate results trong quá trình điều phối.  
- **[Observability](ca://s?q=Observability_module)**: giám sát toàn bộ hoạt động của dispatcher.  

---

## 📊 Contract Types
- **Functional Contract**: dispatcher phải thực hiện đúng chức năng điều phối stage.  
- **Data Contract**: input/output giữa dispatcher và stage phải tuân theo JSON schema chuẩn.  
- **Security Contract**: dispatcher phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contract**: mọi thay đổi dispatcher phải được ghi lại trong ADR và RFC.  

---

## 🛡️ Security
- Dispatcher Contract được giám sát bởi workflow **security.yml**.  
- Input/output của dispatcher phải được kiểm tra để tránh dữ liệu độc hại.  

---

## 📬 Governance
- Dispatcher Contract được duy trì bởi **Architecture Team** và **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ workflow orchestration frameworks (Apache Airflow, Kubernetes Controllers, LangChain Executors), điều chỉnh cho phù hợp với SciOS-NG.

# Stage Contract - SciOS-NG

## 📖 Introduction
**Stage Contract** là thỏa thuận chính thức về cách một stage trong cognitive pipeline hoạt động.  
Mục tiêu: đảm bảo mỗi stage có thể **minh bạch, tái lập, và an toàn**, đồng thời dễ dàng tích hợp với các stage khác.

---

## 🏛️ Responsibilities
- **Definition**: xác định input, output, và logic của stage.  
- **Validation**: kiểm tra dữ liệu trước và sau khi stage chạy.  
- **Execution**: đảm bảo stage được thực thi đúng thứ tự qua **[stage dispatcher](ca://s?q=Stage_dispatcher_module)**.  
- **Observability**: tích hợp log, metrics, và trace cho từng stage.  
- **Governance**: mọi thay đổi stage phải qua **[Architecture RFC](ca://s?q=Architecture_RFC_template)**.  

---

## 🔄 Interaction with Other Components
- **[Pipeline](ca://s?q=Pipeline_module)**: stage là thành phần cơ bản của pipeline.  
- **[Planner](ca://s?q=Planner_module)**: xác định dependency và thứ tự stage.  
- **[Runtime](ca://s?q=Runtime_module)**: thực thi stage reasoning.  
- **[Memory](ca://s?q=Memory_module)**: lưu trữ state và intermediate results.  
- **[Knowledge](ca://s?q=Knowledge_module)**: cung cấp tri thức nền cho stage.  
- **[Observability](ca://s?q=Observability_module)**: giám sát quá trình thực thi stage.  

---

## 📊 Contract Types
- **Functional Contract**: stage phải thực hiện đúng chức năng đã định nghĩa.  
- **Data Contract**: input/output của stage phải tuân theo JSON schema chuẩn.  
- **Security Contract**: stage phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contract**: mọi thay đổi stage phải được ghi lại trong ADR và RFC.  

---

## 🛡️ Security
- Stage Contract được giám sát bởi workflow **security.yml**.  
- Input/output của stage phải được kiểm tra để tránh dữ liệu độc hại.  

---

## 📬 Governance
- Stage Contract được duy trì bởi **Architecture Team** và **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ workflow orchestration frameworks (Apache Airflow, Kubeflow, LangChain Executors), điều chỉnh cho phù hợp với SciOS-NG.

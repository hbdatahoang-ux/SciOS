# Planner Contract - SciOS-NG

## 📖 Introduction
**Planner Contract** là thỏa thuận chính thức về cách SciOS-NG lập kế hoạch cho cognitive pipeline.  
Mục tiêu: đảm bảo việc lập kế hoạch reasoning diễn ra **minh bạch, tái lập, và an toàn**, đồng thời hỗ trợ mở rộng và tối ưu hóa.

---

## 🏛️ Responsibilities
- **Task Decomposition**: phân rã nhiệm vụ thành các stage nhỏ.  
- **Dependency Management**: xác định dependency giữa các stage.  
- **Scheduling**: sắp xếp thứ tự thực thi stage.  
- **Resource Allocation**: phân bổ tài nguyên cho từng stage.  
- **Validation**: kiểm tra kế hoạch trước khi gửi cho **[dispatcher](ca://s?q=Dispatcher_contract)**.  

---

## 🔄 Interaction with Other Components
- **[Pipeline](ca://s?q=Pipeline_module)**: planner tạo kế hoạch cho pipeline reasoning.  
- **[Stage Dispatcher](ca://s?q=Stage_dispatcher_module)**: nhận kế hoạch từ planner để điều phối stage.  
- **[Runtime](ca://s?q=Runtime_module)**: thực thi kế hoạch reasoning.  
- **[Memory](ca://s?q=Memory_module)**: tham chiếu state và dữ liệu để lập kế hoạch.  
- **[Knowledge](ca://s?q=Knowledge_module)**: sử dụng tri thức nền để tối ưu kế hoạch.  
- **[Reflection](ca://s?q=Reflection_module)**: cập nhật kế hoạch dựa trên phản tư.  
- **[Observability](ca://s?q=Observability_module)**: giám sát quá trình lập kế hoạch.  

---

## 📊 Contract Types
- **Functional Contract**: planner phải tạo kế hoạch đầy đủ và hợp lệ cho pipeline.  
- **Data Contract**: kế hoạch phải tuân theo JSON schema chuẩn.  
- **Security Contract**: planner phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contract**: mọi thay đổi planner phải được ghi lại trong ADR và RFC.  

---

## 🛡️ Security
- Planner Contract được giám sát bởi workflow **security.yml**.  
- Input/output của planner phải được kiểm tra để tránh dữ liệu độc hại.  

---

## 📬 Governance
- Planner Contract được duy trì bởi **Architecture Team** và **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ workflow orchestration frameworks (Apache Airflow DAG Planner, Kubernetes Scheduler, LangChain Task Planner), điều chỉnh cho phù hợp với SciOS-NG.

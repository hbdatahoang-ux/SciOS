# Planner - SciOS-NG

## 📖 Introduction
**Planner** là thành phần chịu trách nhiệm điều phối reasoning tasks trong SciOS-NG. Nó phân tích yêu cầu, tạo kế hoạch thực thi, và đảm bảo các dependency giữa các module được xử lý đúng thứ tự.

---

## 🏛️ Responsibilities
- **Task Scheduling**: sắp xếp thứ tự thực thi reasoning tasks.  
- **Dependency Management**: xác định và quản lý dependency giữa các module.  
- **Optimization**: lựa chọn chiến lược thực thi tối ưu (tuần tự hoặc song song).  
- **Integration**: kết nối perception, memory, knowledge, và runtime thành một pipeline hợp lý.  

---

## 🔄 Interaction with Other Components
- **[Kernel](ca://s?q=Kernel_module)**: planner yêu cầu tài nguyên từ kernel để thực thi kế hoạch.  
- **[Runtime](ca://s?q=Runtime_module)**: planner gửi kế hoạch cho runtime để thực thi.  
- **[Pipeline](ca://s?q=Pipeline_module)**: planner là bước trung gian, biến yêu cầu thành pipeline cụ thể.  
- **[Execution](ca://s?q=Execution_module)**: planner phối hợp với execution layer để giám sát quá trình thực thi.  

---

## 🛡️ Security
- Planner được giám sát bởi workflow **[security.yml](ca://s?q=Security_workflow_template)** để phát hiện kế hoạch bất thường.  
- Báo cáo sự cố bảo mật liên quan đến planner qua [SECURITY.md](../../SECURITY.md).  

---

## 📊 Design Principles
- **Transparency**: mọi kế hoạch reasoning đều được ghi log.  
- **Reproducibility**: cùng một input sẽ tạo ra cùng một kế hoạch reasoning.  
- **Resilience**: planner có cơ chế fallback khi gặp lỗi dependency.  
- **Scalability**: hỗ trợ điều phối reasoning ở quy mô lớn.  

---

## 📬 Governance
- Quyết định liên quan đến planner thuộc về **Architecture Team** và **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ hệ thống điều phối phân tán (Apache Airflow, Kubernetes Scheduler), điều chỉnh cho phù hợp với SciOS-NG.

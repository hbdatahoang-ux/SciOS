# Contracts - SciOS-NG

## 📖 Introduction
**Contracts** trong SciOS-NG là các thỏa thuận chính thức giữa các module (kernel, runtime, planner, pipeline, perception, memory, reasoning, reflection, distributed, deployment).  
Mục tiêu: đảm bảo các thành phần có thể tương tác với nhau một cách **minh bạch, tái lập, và an toàn**.

---

## 🏛️ Responsibilities
- **Interface Definition**: xác định API và giao diện giữa các module.  
- **Data Schema**: định nghĩa cấu trúc dữ liệu được trao đổi.  
- **Validation**: kiểm tra input/output để đảm bảo hợp lệ.  
- **Governance**: duy trì consistency giữa các contracts khi hệ thống mở rộng.  

---

## 🔄 Interaction with Other Components
- **[Kernel](ca://s?q=Kernel_module)**: cung cấp contracts về resource allocation.  
- **[Runtime](ca://s?q=Runtime_module)**: sử dụng contracts để thực thi pipeline reasoning.  
- **[Planner](ca://s?q=Planner_module)**: dựa vào contracts để điều phối dependency.  
- **[Pipeline](ca://s?q=Pipeline_module)**: tích hợp contracts để đảm bảo reproducibility.  
- **[Observability](ca://s?q=Observability_module)**: ghi log và trace theo contracts.  

---

## 📊 Contract Types
- **Functional Contracts**: định nghĩa hành vi của module (ví dụ: planner phải trả về kế hoạch hợp lệ).  
- **Data Contracts**: định nghĩa schema dữ liệu (ví dụ: memory phải lưu state theo JSON schema chuẩn).  
- **Security Contracts**: đảm bảo input/output tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contracts**: mọi thay đổi phải qua **[Architecture RFC](ca://s?q=Architecture_RFC_template)**.  

---

## 🛡️ Security
- Contracts được giám sát bởi workflow **security.yml** để phát hiện vi phạm.  
- Báo cáo sự cố bảo mật liên quan đến contracts qua [SECURITY.md](../../SECURITY.md).  

---

## 📬 Governance
- Contracts được duy trì bởi **Architecture Team** và **Core Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ hệ thống phân tán (API contracts, data contracts trong microservices, CNCF projects), điều chỉnh cho phù hợp với SciOS-NG.

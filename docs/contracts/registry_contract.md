# Registry Contract - SciOS-NG

## 📖 Introduction
**Registry Contract** là thỏa thuận chính thức về cách các thành phần (modules, stages, tools) được đăng ký và quản lý trong SciOS-NG.  
Mục tiêu: đảm bảo việc đăng ký và tra cứu thành phần diễn ra **minh bạch, tái lập, và an toàn**.

---

## 🏛️ Responsibilities
- **Registration**: cho phép các module, stage, hoặc tool đăng ký vào hệ thống.  
- **Lookup**: cung cấp cơ chế tra cứu thành phần theo tên hoặc ID.  
- **Validation**: kiểm tra tính hợp lệ của thành phần trước khi đăng ký.  
- **Versioning**: hỗ trợ nhiều phiên bản của cùng một thành phần.  
- **Observability**: ghi log toàn bộ hoạt động đăng ký và tra cứu.  

---

## 🔄 Interaction with Other Components
- **[Stage Dispatcher](ca://s?q=Stage_dispatcher_module)**: sử dụng registry để tra cứu stage cần điều phối.  
- **[Pipeline](ca://s?q=Pipeline_module)**: pipeline tham chiếu registry để xác định các stage hợp lệ.  
- **[Planner](ca://s?q=Planner_module)**: tra cứu registry để lập kế hoạch thực thi.  
- **[Runtime](ca://s?q=Runtime_module)**: lấy thông tin từ registry để thực thi thành phần.  
- **[Observability](ca://s?q=Observability_module)**: giám sát hoạt động registry.  

---

## 📊 Contract Types
- **Functional Contract**: registry phải cho phép đăng ký và tra cứu thành phần một cách nhất quán.  
- **Data Contract**: thông tin thành phần phải tuân theo JSON schema chuẩn.  
- **Security Contract**: registry phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contract**: mọi thay đổi registry phải được ghi lại trong ADR và RFC.  

---

## 🛡️ Security
- Registry Contract được giám sát bởi workflow **security.yml**.  
- Input/output của registry phải được kiểm tra để tránh dữ liệu độc hại.  

---

## 📬 Governance
- Registry Contract được duy trì bởi **Architecture Team** và **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ service registries (Kubernetes API Server, Consul, etcd), điều chỉnh cho phù hợp với SciOS-NG.

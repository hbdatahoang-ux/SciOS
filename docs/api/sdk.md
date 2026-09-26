# SDK Contract - SciOS-NG

## 📖 Introduction
**SDK** là bộ công cụ dành cho lập trình viên để tích hợp và mở rộng SciOS-NG.  
Mục tiêu: đảm bảo SDK cung cấp **API bindings, client libraries, và developer tools** một cách minh bạch, tái lập, và an toàn.

---

## 🏛️ Responsibilities
- **API Bindings**: cung cấp wrapper cho **[kernel API](ca://s?q=Kernel_API_contract)** và **[runtime API](ca://s?q=Runtime_API_contract)**.  
- **Context Management**: hỗ trợ quản lý **[cognitive context](ca://s?q=Cognitive_context_contract)** trong ứng dụng.  
- **Pipeline Control**: cho phép khởi tạo, thực thi, và giám sát pipeline reasoning.  
- **Tool Integration**: hỗ trợ gọi **[tools](ca://s?q=Tool_contract)** từ SDK.  
- **Observability**: cung cấp hooks để log, metrics, và trace.  

---

## 🔄 Supported Languages
- **Python SDK** → dành cho AI/ML workflows.  
- **JavaScript/TypeScript SDK** → dành cho web và Node.js.  
- **Go SDK** → dành cho hệ thống phân tán.  
- **Rust SDK** → dành cho high-performance reasoning.  

---

## 📊 Contract Types
- **Functional Contract**: SDK phải cung cấp đầy đủ API bindings cho kernel và runtime.  
- **Data Contract**: input/output SDK phải tuân theo JSON schema chuẩn.  
- **Security Contract**: SDK phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contract**: mọi thay đổi SDK phải được ghi lại trong ADR và RFC.  

---

## 🛡️ Security
- SDK Contract được giám sát bởi workflow **security.yml**.  
- Input/output SDK phải được kiểm tra để tránh dữ liệu độc hại.  
- SDK phải hỗ trợ cơ chế **authentication** và **authorization**.  

---

## 📬 Governance
- SDK Contract được duy trì bởi **Architecture Team** và **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](./MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ SDK frameworks (TensorFlow SDK, Kubernetes Client SDK, LangChain SDK, Semantic Kernel SDK), điều chỉnh cho phù hợp với SciOS-NG.

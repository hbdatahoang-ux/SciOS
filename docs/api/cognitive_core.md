# Cognitive Core API Contract - SciOS-NG

## 📖 Introduction
**Cognitive Core API** là giao diện trung tâm cho các chức năng nhận thức trong SciOS-NG.  
Mục tiêu: đảm bảo cognitive core có thể **quản lý ngữ cảnh, reasoning, memory, và reflection** một cách minh bạch, tái lập, và an toàn.

---

## 🏛️ Responsibilities
- **Context Management**: duy trì và chia sẻ **[cognitive context](ca://s?q=Cognitive_context_contract)** cho toàn bộ pipeline.  
- **Reasoning Execution**: thực hiện inference qua **[reasoning](ca://s?q=Reasoning_contract)**.  
- **Memory Integration**: kết nối với **[memory](ca://s?q=Memory_contract)** để lưu trữ và truy xuất state.  
- **Knowledge Access**: truy vấn tri thức nền từ **[knowledge](ca://s?q=Knowledge_contract)**.  
- **Reflection Loop**: hỗ trợ phản tư qua **[reflection](ca://s?q=Reflection_contract)**.  
- **Observability**: cung cấp log, metrics, và trace cho cognitive core API.  

---

## 🔄 API Endpoints
- **/context/get** → lấy cognitive context hiện tại.  
- **/context/update** → cập nhật cognitive context.  
- **/reasoning/run** → thực hiện reasoning dựa trên input và tri thức nền.  
- **/memory/read** → truy xuất dữ liệu từ memory.  
- **/memory/write** → ghi dữ liệu vào memory.  
- **/knowledge/query** → truy vấn tri thức nền.  
- **/reflection/run** → chạy vòng phản tư để đánh giá reasoning.  
- **/observability/logs** → lấy log và metrics từ cognitive core.  

---

## 📊 Contract Types
- **Functional Contract**: cognitive core phải cung cấp đầy đủ API cho reasoning pipeline.  
- **Data Contract**: input/output API phải tuân theo JSON schema chuẩn.  
- **Security Contract**: cognitive core phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contract**: mọi thay đổi cognitive core API phải được ghi lại trong ADR và RFC.  

---

## 🛡️ Security
- Cognitive Core API được giám sát bởi workflow **security.yml**.  
- Input/output phải được kiểm tra để tránh dữ liệu độc hại.  
- API phải hỗ trợ cơ chế **authentication** và **authorization**.  

---

## 📬 Governance
- Cognitive Core API Contract được duy trì bởi **Architecture Team** và **Research Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ cognitive architectures (SOAR, ACT-R, LangChain Core, Semantic Kernel), điều chỉnh cho phù hợp với SciOS-NG.

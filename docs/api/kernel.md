# Kernel API Contract - SciOS-NG

## 📖 Introduction
**Kernel API** là giao diện trung tâm của SciOS-NG, cung cấp các endpoint để quản lý cognitive pipeline, memory, knowledge, reasoning, và reflection.  
Mục tiêu: đảm bảo API kernel hoạt động **minh bạch, tái lập, mở rộng, và an toàn**.

---

## 🏛️ Responsibilities
- **Pipeline Control**: khởi tạo, thực thi, và giám sát pipeline reasoning.  
- **Stage Management**: đăng ký, điều phối, và giám sát các stage qua **[dispatcher](ca://s?q=Dispatcher_contract)**.  
- **Memory Access**: cung cấp API để đọc/ghi **[memory](ca://s?q=Memory_contract)**.  
- **Knowledge Integration**: kết nối tri thức nền từ **[knowledge](ca://s?q=Knowledge_contract)**.  
- **Reflection Loop**: hỗ trợ phản tư qua **[reflection](ca://s?q=Reflection_contract)**.  
- **Observability**: tích hợp log, metrics, và trace cho toàn bộ kernel API.  

---

## 🔄 API Endpoints
- **/pipeline/start** → khởi tạo pipeline reasoning.  
- **/pipeline/status** → kiểm tra trạng thái pipeline.  
- **/stage/register** → đăng ký stage mới.  
- **/stage/execute** → thực thi stage reasoning.  
- **/memory/read** → truy xuất dữ liệu từ memory.  
- **/memory/write** → ghi dữ liệu vào memory.  
- **/knowledge/query** → truy vấn tri thức nền.  
- **/reflection/run** → chạy vòng phản tư.  
- **/observability/logs** → lấy log và metrics.  

---

## 📊 Contract Types
- **Functional Contract**: API kernel phải cung cấp đầy đủ endpoint cho pipeline và module.  
- **Data Contract**: input/output API phải tuân theo JSON schema chuẩn.  
- **Security Contract**: API kernel phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contract**: mọi thay đổi API kernel phải được ghi lại trong ADR và RFC.  

---

## 🛡️ Security
- Kernel API được giám sát bởi workflow **security.yml**.  
- Input/output API phải được kiểm tra để tránh dữ liệu độc hại.  
- API phải hỗ trợ cơ chế **authentication** và **authorization**.  

---

## 📬 Governance
- Kernel API Contract được duy trì bởi **Architecture Team** và **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ API design (REST, gRPC, GraphQL), orchestration frameworks (Kubernetes API Server, LangChain Kernel), điều chỉnh cho phù hợp với SciOS-NG.

# Runtime API Contract - SciOS-NG

## 📖 Introduction
**Runtime API** là giao diện cho việc thực thi pipeline reasoning trong SciOS-NG.  
Mục tiêu: đảm bảo runtime có thể **quản lý, giám sát, và phục hồi** quá trình reasoning một cách minh bạch, tái lập, và an toàn.

---

## 🏛️ Responsibilities
- **Pipeline Execution**: thực thi pipeline reasoning theo kế hoạch từ **[planner](ca://s?q=Planner_contract)**.  
- **Stage Execution**: chạy từng stage qua **[dispatcher](ca://s?q=Dispatcher_contract)**.  
- **State Management**: duy trì trạng thái pipeline trong suốt quá trình chạy.  
- **Error Handling**: cung cấp cơ chế phục hồi khi có lỗi.  
- **Observability**: tích hợp log, metrics, và trace cho toàn bộ runtime.  

---

## 🔄 API Endpoints
- **/runtime/start** → khởi động pipeline reasoning.  
- **/runtime/stop** → dừng pipeline reasoning.  
- **/runtime/status** → kiểm tra trạng thái runtime.  
- **/runtime/restart** → khởi động lại pipeline reasoning.  
- **/runtime/stage/execute** → thực thi một stage cụ thể.  
- **/runtime/stage/status** → kiểm tra trạng thái stage.  
- **/runtime/logs** → lấy log và metrics từ runtime.  

---

## 📊 Contract Types
- **Functional Contract**: runtime phải thực thi đầy đủ pipeline reasoning.  
- **Data Contract**: input/output runtime phải tuân theo JSON schema chuẩn.  
- **Security Contract**: runtime phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contract**: mọi thay đổi runtime phải được ghi lại trong ADR và RFC.  

---

## 🛡️ Security
- Runtime API được giám sát bởi workflow **security.yml**.  
- Input/output phải được kiểm tra để tránh dữ liệu độc hại.  
- Runtime phải hỗ trợ cơ chế **authentication** và **authorization**.  

---

## 📬 Governance
- Runtime API Contract được duy trì bởi **Architecture Team** và **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ workflow orchestration frameworks (Kubernetes Runtime, Apache Airflow Executors, LangChain Runtime), điều chỉnh cho phù hợp với SciOS-NG.

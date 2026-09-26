# CLI Contract - SciOS-NG

## 📖 Introduction
**CLI** là giao diện dòng lệnh dành cho lập trình viên và kỹ sư để quản lý SciOS-NG.  
Mục tiêu: đảm bảo CLI cung cấp **các lệnh trực quan, tái lập, và an toàn** để điều khiển pipeline, runtime, memory, và observability.

---

## 🏛️ Responsibilities
- **Pipeline Control**: khởi tạo, dừng, và giám sát pipeline reasoning.  
- **Stage Management**: đăng ký, thực thi, và kiểm tra trạng thái stage.  
- **Memory Access**: đọc/ghi dữ liệu từ **[memory](ca://s?q=Memory_contract)**.  
- **Knowledge Query**: truy vấn tri thức nền từ **[knowledge](ca://s?q=Knowledge_contract)**.  
- **Reflection Loop**: chạy vòng phản tư qua **[reflection](ca://s?q=Reflection_contract)**.  
- **Observability**: hiển thị log, metrics, và trace trực tiếp từ CLI.  

---

## 🔄 CLI Commands
- `scios pipeline start` → khởi động pipeline reasoning.  
- `scios pipeline status` → kiểm tra trạng thái pipeline.  
- `scios stage register <name>` → đăng ký stage mới.  
- `scios stage run <name>` → thực thi một stage cụ thể.  
- `scios memory read <key>` → đọc dữ liệu từ memory.  
- `scios memory write <key> <value>` → ghi dữ liệu vào memory.  
- `scios knowledge query "<question>"` → truy vấn tri thức nền.  
- `scios reflection run` → chạy vòng phản tư.  
- `scios logs` → hiển thị log và metrics.  

---

## 📊 Contract Types
- **Functional Contract**: CLI phải cung cấp đầy đủ lệnh cho pipeline và module.  
- **Data Contract**: input/output CLI phải tuân theo JSON schema chuẩn.  
- **Security Contract**: CLI phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contract**: mọi thay đổi CLI phải được ghi lại trong ADR và RFC.  

---

## 🛡️ Security
- CLI Contract được giám sát bởi workflow **security.yml**.  
- Input/output CLI phải được kiểm tra để tránh dữ liệu độc hại.  
- CLI phải hỗ trợ cơ chế **authentication** và **authorization** khi kết nối với kernel API.  

---

## 📬 Governance
- CLI Contract được duy trì bởi **Architecture Team** và **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](./MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ CLI frameworks (Kubernetes `kubectl`, Docker CLI, LangChain CLI, Semantic Kernel CLI), điều chỉnh cho phù hợp với SciOS-NG.

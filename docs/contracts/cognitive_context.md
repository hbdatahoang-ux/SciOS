# Cognitive Context Contract - SciOS-NG

## 📖 Introduction
**Cognitive Context** là ngữ cảnh nhận thức mà hệ thống SciOS-NG duy trì trong suốt quá trình reasoning.  
Mục tiêu: đảm bảo mọi module đều có thể truy cập và sử dụng ngữ cảnh một cách **minh bạch, tái lập, và an toàn**.

---

## 🏛️ Responsibilities
- **Context Sharing**: cung cấp ngữ cảnh chung cho perception, memory, knowledge, reasoning, và reflection.  
- **State Management**: duy trì trạng thái reasoning xuyên suốt pipeline.  
- **Consistency**: đảm bảo mọi module sử dụng cùng một cognitive context.  
- **Validation**: kiểm tra dữ liệu ngữ cảnh để tránh sai lệch hoặc lỗi logic.  

---

## 🔄 Interaction with Other Components
- **[Perception](ca://s?q=Perception_module)**: thêm dữ liệu cảm nhận vào cognitive context.  
- **[Memory](ca://s?q=Memory_module)**: lưu trữ và truy xuất state từ cognitive context.  
- **[Knowledge](ca://s?q=Knowledge_module)**: cung cấp tri thức nền cho cognitive context.  
- **[Reasoning](ca://s?q=Reasoning_module)**: sử dụng cognitive context để thực hiện inference.  
- **[Reflection](ca://s?q=Reflection_module)**: cập nhật cognitive context sau khi đánh giá reasoning.  
- **[Planner](ca://s?q=Planner_module)**: điều phối task dựa trên cognitive context.  

---

## 📊 Contract Types
- **Functional Contract**: cognitive context phải được duy trì xuyên suốt pipeline.  
- **Data Contract**: cognitive context được định nghĩa theo JSON schema chuẩn.  
- **Security Contract**: mọi dữ liệu ngữ cảnh phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contract**: mọi thay đổi cognitive context phải qua **[Architecture RFC](ca://s?q=Architecture_RFC_template)**.  

---

## 🛡️ Security
- Cognitive context được giám sát bởi workflow **security.yml**.  
- Input/output ngữ cảnh phải được kiểm tra để tránh dữ liệu độc hại.  

---

## 📬 Governance
- Cognitive Context Contract được duy trì bởi **Architecture Team** và **Research Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ cognitive architectures (SOAR, ACT-R, Semantic Kernel, LangChain Context Management), điều chỉnh cho phù hợp với SciOS-NG.

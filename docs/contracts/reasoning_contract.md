# Reasoning Contract - SciOS-NG

## 📖 Introduction
**Reasoning Contract** là thỏa thuận chính thức về cách SciOS-NG thực hiện suy luận (reasoning) dựa trên dữ liệu, memory, và tri thức nền.  
Mục tiêu: đảm bảo reasoning diễn ra **minh bạch, tái lập, và an toàn**, đồng thời hỗ trợ cải thiện liên tục qua reflection loop.

---

## 🏛️ Responsibilities
- **Inference Execution**: thực hiện suy luận dựa trên cognitive context và tri thức nền.  
- **Validation**: kiểm tra logic và dữ liệu đầu ra của reasoning.  
- **Transparency**: ghi log toàn bộ quá trình reasoning để có thể kiểm chứng.  
- **Feedback Integration**: tiếp nhận phản hồi từ **[reflection](ca://s?q=Reflection_module)** và người dùng.  
- **Improvement**: cập nhật reasoning pipeline dựa trên kết quả phản tư.  

---

## 🔄 Interaction with Other Components
- **[Pipeline](ca://s?q=Pipeline_module)**: reasoning là stage trung tâm trong pipeline.  
- **[Memory](ca://s?q=Memory_module)**: sử dụng state và tri thức từ memory để reasoning.  
- **[Knowledge](ca://s?q=Knowledge_module)**: cung cấp tri thức nền cho inference.  
- **[Reflection](ca://s?q=Reflection_module)**: đánh giá và cải thiện reasoning sau khi chạy.  
- **[Planner](ca://s?q=Planner_module)**: điều phối reasoning task trong pipeline.  
- **[Observability](ca://s?q=Observability_module)**: giám sát toàn bộ quá trình reasoning.  

---

## 📊 Contract Types
- **Functional Contract**: reasoning phải tạo ra inference hợp lệ dựa trên input và tri thức nền.  
- **Data Contract**: input/output reasoning phải tuân theo JSON schema chuẩn.  
- **Security Contract**: reasoning phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contract**: mọi thay đổi reasoning phải được ghi lại trong ADR và RFC.  

---

## 🛡️ Security
- Reasoning Contract được giám sát bởi workflow **security.yml**.  
- Input/output reasoning phải được kiểm tra để tránh dữ liệu độc hại hoặc logic sai lệch.  

---

## 📬 Governance
- Reasoning Contract được duy trì bởi **Architecture Team** và **Research Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ cognitive architectures (SOAR, ACT-R, Self-Reflective LLMs, LangChain Reasoning Engines), điều chỉnh cho phù hợp với SciOS-NG.

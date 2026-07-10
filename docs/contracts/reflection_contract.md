# Reflection Contract - SciOS-NG

## 📖 Introduction
**Reflection Contract** là thỏa thuận chính thức về cách SciOS-NG thực hiện phản tư (reflection) sau mỗi lần reasoning.  
Mục tiêu: đảm bảo hệ thống có thể **tự đánh giá, phát hiện lỗi, và cải thiện liên tục** dựa trên kết quả reasoning và phản hồi từ người dùng.

---

## 🏛️ Responsibilities
- **Self-Evaluation**: đánh giá chất lượng reasoning output.  
- **Error Analysis**: phát hiện lỗi logic hoặc dữ liệu.  
- **Feedback Integration**: tiếp nhận phản hồi từ người dùng hoặc benchmark.  
- **Learning Loop**: cập nhật **[memory](ca://s?q=Memory_contract)** và **[knowledge](ca://s?q=Knowledge_contract)** dựa trên kết quả phản tư.  
- **Pipeline Update**: điều chỉnh **[pipeline](ca://s?q=Pipeline_contract)** reasoning để cải thiện hiệu quả.  

---

## 🔄 Interaction with Other Components
- **[Pipeline](ca://s?q=Pipeline_module)**: reflection đánh giá toàn bộ pipeline sau khi chạy.  
- **[Reasoning](ca://s?q=Reasoning_contract)**: reflection phân tích và cải thiện reasoning output.  
- **[Memory](ca://s?q=Memory_contract)**: cập nhật state và durable facts sau phản tư.  
- **[Knowledge](ca://s?q=Knowledge_contract)**: bổ sung tri thức mới từ kết quả reflection.  
- **[Planner](ca://s?q=Planner_contract)**: điều chỉnh kế hoạch dựa trên phản tư.  
- **[Observability](ca://s?q=Observability_module)**: giám sát và ghi log toàn bộ quá trình reflection.  

---

## 📊 Contract Types
- **Functional Contract**: reflection phải thực hiện đầy đủ các bước đánh giá và cải thiện.  
- **Data Contract**: dữ liệu reflection phải tuân theo JSON schema chuẩn.  
- **Security Contract**: reflection phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contract**: mọi thay đổi reflection phải được ghi lại trong ADR và RFC.  

---

## 🛡️ Security
- Reflection Contract được giám sát bởi workflow **security.yml**.  
- Input/output của reflection phải được kiểm tra để tránh dữ liệu độc hại hoặc thao túng.  

---

## 📬 Governance
- Reflection Contract được duy trì bởi **Architecture Team** và **Research Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ meta-learning frameworks, reflective AI architectures (SOAR, ACT-R, Self-Reflective LLMs), điều chỉnh cho phù hợp với SciOS-NG.

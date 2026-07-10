# ADR-0001: Cognitive Pipeline

## 📖 Context
SciOS-NG cần một cơ chế để xử lý dữ liệu từ perception, memory, knowledge, và reasoning theo một luồng thống nhất.  
Mục tiêu: đảm bảo reasoning có thể **minh bạch, tái lập, mở rộng, và phản tư**.

---

## 🏛️ Decision
- Thiết kế một **cognitive pipeline** gồm các bước:
  1. **[Perception](ca://s?q=Perception_module)**: tiếp nhận và chuẩn hóa dữ liệu.  
  2. **[Memory](ca://s?q=Memory_module)**: lưu trữ state và cache reasoning.  
  3. **[Knowledge](ca://s?q=Knowledge_module)**: cung cấp tri thức nền.  
  4. **[Reasoning](ca://s?q=Reasoning_module)**: thực hiện inference và decision making.  
  5. **[Reflection](ca://s?q=Reflection_module)**: tự đánh giá và cải thiện pipeline.  
  6. **[Planner](ca://s?q=Planner_module)**: điều phối task và dependency.  
  7. **[Runtime](ca://s?q=Runtime_module)**: thực thi pipeline reasoning.  
  8. **[Observability](ca://s?q=Observability_module)**: giám sát và ghi log toàn bộ pipeline.  

- Cognitive pipeline được triển khai theo **modular architecture**, cho phép thay thế hoặc mở rộng từng bước mà không ảnh hưởng đến toàn hệ thống.  

---

## 📊 Consequences
### Positive
- **Transparency**: mọi bước reasoning đều có thể quan sát và kiểm chứng.  
- **Reproducibility**: cùng một input sẽ tạo ra cùng một output.  
- **Scalability**: pipeline có thể mở rộng từ local đến distributed cloud.  
- **Resilience**: hệ thống có cơ chế phục hồi khi gặp lỗi.  

### Negative
- **Complexity**: pipeline nhiều bước có thể làm tăng độ phức tạp.  
- **Overhead**: cần thêm tài nguyên để duy trì observability và reflection.  

---

## 🛡️ Security
- Cognitive pipeline phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- Input/output ở mỗi bước đều được kiểm tra để tránh dữ liệu độc hại.  

---

## 📬 Status
- **Accepted**: Cognitive pipeline là kiến trúc chính thức của SciOS-NG.  

---

## 📬 Governance
- Quyết định này thuộc về **Architecture Team** và **Research Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ cognitive architectures (SOAR, ACT-R, Semantic Kernel), điều chỉnh cho phù hợp với SciOS-NG.

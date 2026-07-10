# Tool Use - SciOS-NG

## 📖 Introduction
Trong SciOS-NG, **tool use** là cơ chế cho phép hệ thống gọi và phối hợp các công cụ bên ngoài để hỗ trợ reasoning.  
Các công cụ này bao gồm **search**, **memory**, **execution helpers**, và **integration modules**.

---

## 🏛️ Responsibilities
- **Invocation**: gọi đúng công cụ theo yêu cầu reasoning.  
- **Validation**: kiểm tra input/output của công cụ để đảm bảo tính hợp lệ.  
- **Integration**: kết nối kết quả từ công cụ vào pipeline reasoning.  
- **Transparency**: ghi log toàn bộ quá trình sử dụng công cụ.  

---

## 🔄 Tool Categories
- **[Search Web](ca://s?q=Search_web_tool)**: tìm kiếm thông tin mới nhất, chính xác, có thẩm quyền.  
- **[Search Healthcare](ca://s?q=Search_healthcare_tool)**: tra cứu thông tin y tế đáng tin cậy.  
- **[Memory Durable Fact](ca://s?q=Memory_durable_fact_tool)**: lưu trữ và truy xuất thông tin lâu dài.  
- **[Graphic Art](ca://s?q=Graphic_art_tool)**: tạo hoặc chỉnh sửa hình ảnh minh họa.  
- **[Compose Email](ca://s?q=Compose_email_tool)**: soạn thảo và gửi email.  
- **[Search Flights](ca://s?q=Search_flights_tool)**: tìm kiếm thông tin chuyến bay.  
- **[Fetch Web Content](ca://s?q=Fetch_web_content_tool)**: lấy nội dung từ URL.  
- **[Multi Tool Use](ca://s?q=Multi_tool_use)**: chạy nhiều công cụ song song.  

---

## 📊 Workflow Integration
1. **Planner** xác định công cụ cần dùng.  
2. **Kernel** cấp phát tài nguyên cho tool invocation.  
3. **Runtime** gọi công cụ và nhận kết quả.  
4. **Pipeline** tích hợp kết quả vào reasoning.  

---

## 🛡️ Security
- Tất cả tool use được giám sát bởi workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- Input và output của công cụ phải được kiểm tra để tránh dữ liệu độc hại.  
- Báo cáo sự cố bảo mật qua [SECURITY.md](../../SECURITY.md).  

---

## 📬 Governance
- Quyết định liên quan đến tool use thuộc về **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ hệ thống AI orchestration (LangChain, Semantic Kernel), điều chỉnh cho phù hợp với SciOS-NG.

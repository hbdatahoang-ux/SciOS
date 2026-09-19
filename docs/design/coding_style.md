# Coding Style - SciOS-NG

## 📖 Introduction
Coding style trong SciOS-NG được thiết kế để đảm bảo **tính nhất quán, dễ đọc, dễ bảo trì, và minh bạch** trong toàn bộ codebase.  
Mục tiêu: giúp developer cộng tác hiệu quả và giảm thiểu lỗi.

---

## 🏛️ General Principles
- **[Consistency](ca://s?q=Coding_consistency_principle)**: mọi file và module phải tuân theo cùng một chuẩn.  
- **[Readability](ca://s?q=Coding_readability_principle)**: code phải dễ hiểu, dễ theo dõi.  
- **[Maintainability](ca://s?q=Coding_maintainability_principle)**: dễ dàng sửa đổi và mở rộng.  
- **[Transparency](ca://s?q=Transparency_principle)**: mọi logic quan trọng phải được ghi chú rõ ràng.  

---

## 🔤 Naming Conventions
- **Variables**: `snake_case` cho Python, `camelCase` cho JavaScript/TypeScript.  
- **Classes**: `PascalCase`.  
- **Constants**: `UPPER_CASE_WITH_UNDERSCORES`.  
- **Functions**: `snake_case` (Python), `camelCase` (JS/TS).  

---

## 📐 Formatting
- **Indentation**: 4 spaces cho Python, 2 spaces cho JS/TS.  
- **Line Length**: tối đa 100 ký tự.  
- **Braces**: mở cùng dòng, đóng xuống dòng mới (JS/TS).  
- **Imports**: sắp xếp theo nhóm (standard, third-party, local).  

---

## 📝 Documentation
- **Docstrings**: dùng chuẩn Google hoặc NumPy cho Python.  
- **Comments**: ngắn gọn, giải thích logic phức tạp.  
- **Public APIs**: phải có mô tả rõ ràng về input/output.  

---

## ✅ Testing
- **Unit Tests**: bắt buộc cho mọi module.  
- **Naming**: test function theo dạng `test_functionality`.  
- **Coverage**: tối thiểu 80%, được kiểm tra qua workflow **[coverage.yml](ca://s?q=Coverage_workflow_template)**.  

---

## 🛡️ Security
- Code phải tuân thủ chuẩn **[security.yml](ca://s?q=Security_workflow_template)**.  
- Không hardcode secrets, dùng environment variables hoặc secret management.  

---

## 📬 Governance
- Quy tắc coding style được duy trì bởi **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ PEP8 (Python), ESLint/Prettier (JS/TS), và CNCF coding guidelines, điều chỉnh cho phù hợp với SciOS-NG.

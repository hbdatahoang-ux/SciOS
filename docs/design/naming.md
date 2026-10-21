# Naming - SciOS-NG

## 📖 Introduction
Quy tắc đặt tên trong SciOS-NG được thiết kế để đảm bảo **tính nhất quán, dễ đọc, dễ bảo trì, và minh bạch**.  
Mục tiêu: giúp developer và researcher dễ dàng hiểu và sử dụng các thành phần của hệ thống.

---

## 🏛️ General Principles
- **[Consistency](ca://s?q=Coding_consistency_principle)**: mọi tên phải tuân theo cùng một chuẩn.  
- **[Clarity](ca://s?q=Coding_readability_principle)**: tên phải mô tả rõ ràng chức năng hoặc dữ liệu.  
- **[Predictability](ca://s?q=Predictability_principle)**: người dùng có thể đoán được vai trò của thành phần qua tên.  
- **[Transparency](ca://s?q=Transparency_principle)**: tên không gây mơ hồ hoặc ẩn ý.  

---

## 🔤 Naming Conventions

### Variables & Functions
- **Python**: `snake_case` (ví dụ: `process_data`, `user_id`).  
- **JavaScript/TypeScript**: `camelCase` (ví dụ: `fetchData`, `userId`).  

### Classes & Modules
- **Classes**: `PascalCase` (ví dụ: `ReasoningEngine`, `MemoryManager`).  
- **Modules**: `snake_case` cho Python, `kebab-case` cho JS/TS.  

### Constants
- **UPPER_CASE_WITH_UNDERSCORES** (ví dụ: `MAX_RETRIES`, `DEFAULT_TIMEOUT`).  

### Files & Directories
- **snake_case** cho Python (`reasoning_layer.py`).  
- **kebab-case** cho JS/TS (`reasoning-layer.ts`).  
- **Directories**: mô tả chức năng, không viết tắt (`architecture`, `design`, `execution`).  

---

## 📝 Documentation & Contracts
- **Public APIs**: tên phải rõ ràng, không viết tắt khó hiểu.  
- **Contracts**: schema fields dùng `snake_case`.  
- **Experiment Reports**: đặt tên theo chuẩn `experiment_<topic>_<date>.md`.  

---

## ✅ Testing
- **Test Functions**: `test_<functionality>` (ví dụ: `test_pipeline_execution`).  
- **Test Files**: `test_<module>.py` hoặc `test-<module>.ts`.  

---

## 🛡️ Security
- Không dùng tên mơ hồ hoặc dễ gây nhầm lẫn.  
- Tích hợp với workflow **[security.yml](ca://s?q=Security_workflow_template)** để kiểm tra naming trong code review.  

---

## 📬 Governance
- Quy tắc naming được duy trì bởi **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ PEP8 (Python), ESLint/Prettier (JS/TS), và CNCF naming guidelines, điều chỉnh cho phù hợp với SciOS-NG.

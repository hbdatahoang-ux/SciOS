# Plugin Development Tutorial - SciOS-NG

## 📖 Introduction
Trong SciOS-NG, **plugin** là cách mở rộng hệ thống bằng cách thêm công cụ, stage, hoặc logic mới.  
Mục tiêu: giúp nhà phát triển tạo plugin tùy chỉnh để tích hợp dịch vụ bên ngoài hoặc bổ sung khả năng reasoning.

---

## 🛠️ Prerequisites
- Đã cài đặt **SciOS-NG SDK** và **CLI**.  
- Hiểu cơ bản về **[tool contract](ca://s?q=Tool_contract)** và **[stage contract](ca://s?q=Stage_contract)**.  
- Ngôn ngữ lập trình: Python hoặc Node.js.  

---

## 🚀 Steps to Build a Plugin

### 1. Define Plugin Logic
Tạo file `plugins/my_plugin.py`:
```python
class MyPlugin:
    def run(self, input_data):
        # Custom plugin logic
        return {"output": f"MyPlugin processed {input_data}"}

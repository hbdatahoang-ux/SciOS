# Custom Memory Tutorial - SciOS-NG

## 📖 Introduction
Trong SciOS-NG, **[memory](ca://s?q=Memory_contract)** là thành phần lưu trữ state, cache, và tri thức lâu dài.  
Bạn có thể tạo **Custom Memory** để quản lý dữ liệu đặc thù, tối ưu hóa hiệu năng, hoặc tích hợp với hệ thống lưu trữ bên ngoài.

---

## 🛠️ Prerequisites
- Đã cài đặt **SciOS-NG SDK** và **CLI**.  
- Hiểu cơ bản về **[pipeline](ca://s?q=Pipeline_contract)** và **[reasoning](ca://s?q=Reasoning_contract)**.  
- Ngôn ngữ lập trình: Python hoặc Node.js.  

---

## 🚀 Steps to Build a Custom Memory

### 1. Define Memory Logic
Tạo file `memory/custom_memory.py`:
```python
class CustomMemory:
    def __init__(self):
        self.store = {}

    def read(self, key):
        return self.store.get(key, None)

    def write(self, key, value):
        self.store[key] = value
        return {"status": "success", "key": key}

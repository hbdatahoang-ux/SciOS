# Custom Tool Tutorial - SciOS-NG

## 📖 Introduction
Trong SciOS-NG, **[tools](ca://s?q=Tool_contract)** là các thành phần hỗ trợ pipeline reasoning (ví dụ: search, memory, graphic, email).  
Bạn có thể tạo **Custom Tool** để tích hợp dịch vụ bên ngoài hoặc logic đặc thù vào pipeline.

---

## 🛠️ Prerequisites
- Đã cài đặt **SciOS-NG SDK** và **CLI**.  
- Hiểu cơ bản về **[registry](ca://s?q=Registry_contract)** và **[dispatcher](ca://s?q=Dispatcher_contract)**.  
- Ngôn ngữ lập trình: Python hoặc Node.js.  

---

## 🚀 Steps to Build a Custom Tool

### 1. Define Tool Logic
Tạo file `tools/custom_tool.py`:
```python
class CustomTool:
    def run(self, input_data):
        # Custom logic
        result = f"Custom processed: {input_data}"
        return {"output": result}

# Custom Stage Tutorial - SciOS-NG

## 📖 Introduction
Trong SciOS-NG, **[stage](ca://s?q=Stage_contract)** là đơn vị xử lý cơ bản trong pipeline.  
Bạn có thể tạo **Custom Stage** để thêm logic riêng, tích hợp công cụ, hoặc xử lý dữ liệu đặc thù.

---

## 🛠️ Prerequisites
- Đã cài đặt **SciOS-NG CLI** và **SDK**.  
- Hiểu cơ bản về **[pipeline](ca://s?q=Pipeline_contract)** và **[dispatcher](ca://s?q=Dispatcher_contract)**.  
- Ngôn ngữ lập trình: Python hoặc Node.js.  

---

## 🚀 Steps to Build a Custom Stage

### 1. Define Stage Logic
Tạo file `stages/custom_stage.py`:
```python
class CustomStage:
    def run(self, input_data):
        # Custom logic
        processed = input_data.upper()
        return {"result": processed}

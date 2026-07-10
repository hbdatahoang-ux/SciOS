# Build Your First Pipeline - SciOS-NG

## 📖 Introduction
Trong hướng dẫn này, bạn sẽ học cách xây dựng một **cognitive pipeline** trong SciOS-NG.  
Pipeline là chuỗi các **[stages](ca://s?q=Stage_contract)** được điều phối bởi **[dispatcher](ca://s?q=Dispatcher_contract)** và lập kế hoạch bởi **[planner](ca://s?q=Planner_contract)**.

---

## 🛠️ Prerequisites
- Đã cài đặt **SciOS-NG Kernel** và **CLI**.  
- Hiểu cơ bản về **[pipeline](ca://s?q=Pipeline_contract)** và **[stage](ca://s?q=Stage_contract)**.  
- Python hoặc Node.js SDK để viết custom stages.  

---

## 🚀 Steps to Build a Pipeline

### 1. Define Stages
Tạo file `stages/example_stage.py`:
```python
class ExampleStage:
    def run(self, input_data):
        return {"result": f"Processed {input_data}"}

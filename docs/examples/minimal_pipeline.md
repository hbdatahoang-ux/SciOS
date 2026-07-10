# Minimal Pipeline Example - SciOS-NG

## 📖 Introduction
Ví dụ này cho thấy cách xây dựng một **pipeline tối giản** trong SciOS-NG.  
Pipeline này chỉ có một stage đơn giản, giúp bạn làm quen với **[pipeline](ca://s?q=Pipeline_contract)** và **[stage](ca://s?q=Stage_contract)**.

---

## 🚀 Steps

### 1. Define Stage
Tạo file `stages/minimal_stage.py`:
```python
class MinimalStage:
    def run(self, input_data):
        return {"result": f"Hello, {input_data}!"}

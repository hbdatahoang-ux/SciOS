# Planner Demo - SciOS-NG

## 📖 Introduction
Ví dụ này cho thấy cách **[planner](ca://s?q=Planner_contract)** hoạt động trong SciOS-NG.  
Planner chịu trách nhiệm xác định **thứ tự stage**, **dependency**, và **tool invocation** trong pipeline reasoning.

---

## 🚀 Demo Steps

### 1. Define Stages
Tạo file `stages/alpha_stage.py`:
```python
class AlphaStage:
    def run(self, input_data):
        return {"alpha_result": input_data + " processed by Alpha"}

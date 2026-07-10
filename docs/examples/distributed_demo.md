# Distributed Pipeline Demo - SciOS-NG

## 📖 Introduction
Ví dụ này cho thấy cách SciOS-NG hỗ trợ **distributed execution** cho pipeline reasoning.  
Distributed pipeline cho phép nhiều **[stages](ca://s?q=Stage_contract)** chạy song song trên các node khác nhau, được điều phối bởi **[dispatcher](ca://s?q=Dispatcher_contract)** và lập kế hoạch bởi **[planner](ca://s?q=Planner_contract)**.

---

## 🚀 Demo Steps

### 1. Define Stages
Tạo file `stages/node_stage.py`:
```python
class NodeStage:
    def run(self, input_data):
        return {"node_result": f"Processed {input_data} on distributed node"}

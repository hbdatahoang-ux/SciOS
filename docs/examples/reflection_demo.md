# Reflection Demo - SciOS-NG

## 📖 Introduction
Ví dụ này cho thấy cách **[reflection](ca://s?q=Reflection_contract)** hoạt động trong SciOS-NG.  
Reflection là vòng lặp phản tư, giúp pipeline **đánh giá kết quả reasoning, phát hiện lỗi, và cải thiện logic**.

---

## 🚀 Demo Steps

### 1. Define Reasoning Stage
Tạo file `stages/reasoning_stage.py`:
```python
class ReasoningStage:
    def run(self, input_data):
        return {"answer": f"Initial reasoning on {input_data}"}

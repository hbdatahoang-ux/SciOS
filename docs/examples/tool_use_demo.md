# Tool Use Demo - SciOS-NG

## 📖 Introduction
Ví dụ này cho thấy cách pipeline reasoning trong SciOS-NG sử dụng **[tools](ca://s?q=Tool_contract)** để mở rộng khả năng xử lý.  
Tools có thể là search, memory, graphic, email, hoặc custom tool do bạn định nghĩa.

---

## 🚀 Demo Steps

### 1. Define a Stage with Tool Use
Tạo file `stages/tool_stage.py`:
```python
from tools import search_web

class ToolStage:
    def run(self, input_data):
        # Call search tool
        result = search_web({"query": input_data})
        return {"search_result": result}

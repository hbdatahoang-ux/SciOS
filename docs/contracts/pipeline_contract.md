# Pipeline Contract - SciOS-NG

## 📖 Introduction
**Pipeline Contract** là thỏa thuận chính thức về cách các pipeline reasoning trong SciOS-NG được thiết kế và vận hành.  
Mục tiêu: đảm bảo pipeline reasoning có thể **minh bạch, tái lập, mở rộng, và an toàn**.

---

## 🏛️ Responsibilities
- **Definition**: xác định cấu trúc pipeline (các stage, dependency, input/output).  
- **Execution**: đảm bảo pipeline được thực thi đúng thứ tự qua **[stage dispatcher](ca://s?q=Stage_dispatcher_module)**.  
- **Validation**: kiểm tra dữ liệu giữa các stage để đảm bảo hợp lệ.  
- **Observability**: tích hợp log, metrics, và trace cho toàn bộ pipeline.  
- **Governance**: mọi thay đổi pipeline phải qua **[Architecture RFC](ca://s?q=Architecture_RFC_template)**.  

---

## 🔄 Interaction with Other Components
- **[Planner](ca://s?q=Planner_module)**: tạo kế hoạch pipeline dựa trên cognitive context.  
- **[Runtime](ca://s?q=Runtime_module)**: thực thi pipeline reasoning.  
- **[Memory](ca://s?q=Memory_module)**: lưu trữ state và intermediate results.  
- **[Knowledge](ca://s?q=Knowledge_module)**: cung cấp tri thức nền cho pipeline.  
- **[Reflection](ca://s?q=Reflection_module)**: đánh giá và cải thiện pipeline sau khi chạy.  
- **[Observability](ca://s?q=Observability_module)**: giám sát toàn bộ pipeline execution.  

---

## 📊 Contract Types
- **Functional Contract**: pipeline phải thực thi đầy đủ các stage đã định nghĩa.  
- **Data Contract**: input/output giữa các stage phải tuân theo JSON schema chuẩn.  
- **Security Contract**: pipeline phải tuân thủ workflow **[security.yml](ca://s?q=Security_workflow_template)**.  
- **Governance Contract**: mọi thay đổi pipeline phải được ghi lại trong ADR và RFC.  

---

## 🛡️ Security
- Pipeline Contract được giám sát bởi workflow **security.yml**.  
- Input/output của pipeline phải được kiểm tra để tránh dữ liệu độc hại.  

---

## 📬 Governance
- Pipeline Contract được duy trì bởi **Architecture Team** và **Engineering Team**.  
- Maintainers được liệt kê trong [MAINTAINERS.md](../../MAINTAINERS.md).  

---

## 🙏 Attribution
Dựa trên best practices từ workflow orchestration frameworks (Apache Airflow, Kubeflow, LangChain Executors), điều chỉnh cho phù hợp với SciOS-NG.

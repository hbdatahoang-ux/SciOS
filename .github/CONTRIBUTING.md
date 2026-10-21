# Contributing to SciOS-NG

Xin chào 👋 và cảm ơn bạn đã quan tâm đến việc đóng góp cho **SciOS-NG**!  
Dự án này kết hợp giữa **engineering** và **research**, vì vậy chúng tôi có quy trình rõ ràng để đảm bảo chất lượng và tính minh bạch.

---

## 📌 Quy tắc chung
- Tôn trọng cộng đồng và tuân thủ [Code of Conduct](CODE_OF_CONDUCT.md).
- Luôn mở issue trước khi gửi Pull Request (PR).
- PR phải đi kèm với test, docs, và checklist đầy đủ.
- Review sẽ được gán tự động theo [CODEOWNERS](CODEOWNERS).

---

## 🐞 Báo cáo lỗi
- Sử dụng template **[Bug Report](ca://s?q=Bug_report_template)** trong `.github/ISSUE_TEMPLATE/engineering/`.
- Cung cấp mô tả chi tiết, bước tái hiện, và log nếu có.
- Gắn nhãn `bug`.

---

## ✨ Yêu cầu tính năng
- Sử dụng template **[Feature Request](ca://s?q=Feature_request_template)**.
- Giải thích rõ nhu cầu, giá trị, và tác động.
- Gắn nhãn `feature`.

---

## 🛠️ Thay đổi thiết kế
- Sử dụng template **[Design Change](ca://s?q=Design_change_template)** cho thay đổi nhỏ.
- Sử dụng template **[Architecture RFC](ca://s?q=Architecture_RFC_template)** cho thay đổi lớn.
- Gắn nhãn `architecture`.

---

## 📑 Nghiên cứu
- Sử dụng template **[Research Proposal](ca://s?q=Research_proposal_template)** cho ý tưởng nghiên cứu.
- Sử dụng template **[Benchmark Proposal](ca://s?q=Benchmark_proposal_template)** cho benchmark mới.
- Sử dụng template **[Experiment Report](ca://s?q=Experiment_report_template)** để ghi lại kết quả thực nghiệm.
- Gắn nhãn `research`.

---

## 📖 Tài liệu
- Sử dụng template **[Documentation Report](ca://s?q=Documentation_report_template)**.
- Đảm bảo docs được build thành công với workflow `docs.yml`.

---

## 🔒 Bảo mật
- Báo cáo qua template **[Security Report](ca://s?q=Security_report_template)**.
- Không public lỗ hổng, hãy theo quy trình trong [SECURITY.md](.github/SECURITY.md).

---

## 🚀 Quy trình Pull Request
1. Fork repository và tạo branch mới từ `develop`.
2. Commit theo chuẩn [Conventional Commits](https://www.conventionalcommits.org).
3. Chạy đầy đủ workflow:  
   - **CI** (`ci.yml`)  
   - **Lint** (`lint.yml`)  
   - **Coverage** (`coverage.yml`)  
   - **Docs** (`docs.yml`)  
   - **Benchmarks** (`benchmarks.yml`)  
   - **Security** (`security.yml`)
4. Mở PR và liên kết với issue tương ứng.
5. Đảm bảo checklist trong PR template được tick đầy đủ.

---

## 🌙 Nightly & Release
- Workflow **[nightly.yml](ca://s?q=Nightly_build_workflow)** chạy hằng đêm để kiểm tra ổn định.
- Workflow **[release.yml](ca://s?q=Release_workflow_template)** tạo release tự động khi merge vào `main`.

---

## ✅ Checklist trước khi gửi PR
- [ ] Issue liên quan đã được mở.  
- [ ] Code đã được lint và test.  
- [ ] Coverage không giảm.  
- [ ] Docs đã được cập nhật.  
- [ ] Benchmark không bị thoái hóa.  
- [ ] Reviewers đã được gán tự động qua CODEOWNERS.  

---

Cảm ơn bạn đã đóng góp cho **SciOS-NG** 💙  
Mọi đóng góp đều giúp dự án tiến xa hơn!

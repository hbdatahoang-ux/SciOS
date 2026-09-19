# Security Policy

## 🔒 Reporting a Vulnerability
Nếu bạn phát hiện lỗ hổng bảo mật trong **SciOS-NG**, vui lòng báo cáo một cách có trách nhiệm:
- Không công khai thông tin lỗ hổng trong issue hoặc PR.
- Gửi báo cáo qua email cá nhân: **hbdatahoang@gmail.com**
- Hoặc gửi báo cáo qua địa chỉ dự án: **security@scios-ng.org**
- Ngoài ra, có thể sử dụng template **[Security Report](ca://s?q=Security_report_template)** trong `.github/ISSUE_TEMPLATE/engineering/`.

---

## ✅ Responsible Disclosure
- Chúng tôi cam kết phản hồi trong vòng **72 giờ** kể từ khi nhận báo cáo.
- Lỗ hổng sẽ được phân loại theo mức độ nghiêm trọng (Critical, High, Medium, Low).
- Contributor sẽ được ghi nhận nếu báo cáo hợp lệ và giúp cải thiện dự án.

---

## 🛡️ Security Workflows
Dự án có các workflow bảo mật tự động:
- **[security.yml](ca://s?q=Security_workflow_template)** → quét dependency và phân tích mã nguồn bằng CodeQL, Bandit, Trivy.
- **[dependency-update.yml](ca://s?q=Dependency_update_workflow)** → cập nhật dependency định kỳ và kiểm tra bằng Safety.
- **[dependency-review.yml](ca://s?q=Dependency_review_workflow)** → phân tích thay đổi dependency trong PR.

---

## 📜 Scope
Chính sách này áp dụng cho:
- Toàn bộ codebase trong repository SciOS-NG.
- Các workflow CI/CD liên quan đến bảo mật.
- Các dependency được sử dụng trong dự án.

---

## ⚖️ Enforcement
- Lỗ hổng nghiêm trọng sẽ được xử lý khẩn cấp và có thể dẫn đến việc phát hành bản vá ngay lập tức.
- Contributor cố tình khai thác hoặc công khai lỗ hổng mà không tuân thủ quy trình sẽ bị xử lý theo [Code of Conduct](CODE_OF_CONDUCT.md).

---

## 🙏 Attribution
Dựa trên các chuẩn bảo mật mã nguồn mở (OWASP, CNCF Security Guidelines), điều chỉnh cho phù hợp với SciOS-NG.

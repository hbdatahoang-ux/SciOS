# Governance - SciOS-NG

## 🎯 Purpose
Tài liệu này định nghĩa cơ chế quản trị của **SciOS-NG**, đảm bảo dự án được phát triển minh bạch, có trách nhiệm, và bền vững.

---

## 👥 Roles and Responsibilities

### Core Team
- Quản lý định hướng tổng thể của dự án.
- Duy trì chất lượng code và nghiên cứu.
- Xử lý các quyết định chiến lược.
- Thành viên: @SciOS-NG/core-team

### Engineering Team
- Chịu trách nhiệm về **[engineering templates](ca://s?q=Engineering_team_codeowners)**, CI/CD, và runtime.
- Đảm bảo codebase ổn định, hiệu năng cao.

### Architecture Team
- Quản lý **[architecture RFCs](ca://s?q=Architecture_RFC_template)** và thiết kế hệ thống.
- Đưa ra quyết định về thay đổi lớn trong kiến trúc.

### Research Team
- Phát triển **[research proposals](ca://s?q=Research_proposal_template)**, **[benchmark proposals](ca://s?q=Benchmark_proposal_template)**, và **[experiment reports](ca://s?q=Experiment_report_template)**.
- Đảm bảo tính khoa học và tái lập.

### DevOps Team
- Quản lý **[workflows](ca://s?q=CI_workflow_template)**: CI, lint, coverage, docs, benchmarks, security, release, nightly.
- Đảm bảo pipeline hoạt động liên tục.

### Docs Team
- Duy trì và phát triển **[documentation](ca://s?q=Docs_workflow_template)**.
- Đảm bảo tài liệu đầy đủ, dễ hiểu, và cập nhật.

### Security Team
- Quản lý **[security reports](ca://s?q=Security_report_template)** và quy trình bảo mật.
- Đảm bảo dự án an toàn trước lỗ hổng.

---

## 🗳️ Decision Making
- **Minor changes**: được quyết định bởi nhóm phụ trách (engineering, docs, research…).
- **Major changes**: yêu cầu mở **RFC** qua template **[Architecture RFC](ca://s?q=Architecture_RFC_template)**.
- **Consensus model**: ưu tiên đồng thuận, nếu không đạt → core team quyết định cuối cùng.

---

## 🔄 Workflow Integration
- Mọi thay đổi phải đi qua **Pull Request** và được review bởi **CODEOWNERS**.
- CI/CD workflow bắt buộc phải pass trước khi merge.
- Nightly build và benchmark đảm bảo tính ổn định dài hạn.

---

## 📜 Transparency
- Tất cả quyết định quan trọng được ghi lại trong repo (RFCs, ADRs).
- Discussions mở cho cộng đồng qua [GitHub Discussions](https://github.com/SciOS-NG/SciOS/discussions).

---

## ⚖️ Conflict Resolution
- Tranh chấp nhỏ: giải quyết trong nhóm phụ trách.
- Tranh chấp lớn: escalated lên core team.
- Core team có quyền quyết định cuối cùng.

---

## 🌍 Community Involvement
- Contributor được khuyến khích tham gia qua issue, PR, và discussions.
- Quy trình đóng góp chi tiết trong [CONTRIBUTING.md](CONTRIBUTING.md).
- Quy tắc ứng xử trong [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## 🙏 Attribution
Dựa trên các mô hình quản trị cộng đồng mã nguồn mở (Apache, CNCF, Contributor Covenant), điều chỉnh cho phù hợp với SciOS-NG.

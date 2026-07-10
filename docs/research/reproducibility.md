# Reproducibility Guidelines

Tài liệu này mô tả các nguyên tắc và quy trình để đảm bảo khả năng **tái lập** trong nghiên cứu của dự án **SciOS**.

## Nguyên tắc chính

- **[Tính minh bạch](ca://s?q=Explain_transparency_in_research)**: Công khai toàn bộ dữ liệu, mã nguồn và quy trình thí nghiệm.
- **[Khả năng tái lập](ca://s?q=Explain_reproducibility_in_research)**: Mọi thí nghiệm phải có hướng dẫn chi tiết để người khác có thể thực hiện lại.
- **[Chuẩn hóa](ca://s?q=Explain_standardization_in_research)**: Sử dụng định dạng thống nhất cho dữ liệu, báo cáo và kết quả.
- **[Kiểm chứng độc lập](ca://s?q=Explain_independent_validation_in_research)**: Khuyến khích các nhóm nghiên cứu khác xác nhận kết quả.

## Quy trình tái lập

1. **[Chuẩn bị dữ liệu](ca://s?q=Explain_data_preparation)**  
   - Tập dữ liệu phải được mô tả trong `datasets.md`.  
   - Bao gồm nguồn gốc, định dạng, và các bước tiền xử lý.

2. **[Thiết lập môi trường](ca://s?q=Explain_research_environment_setup)**  
   - Ghi rõ phiên bản phần mềm, thư viện, và cấu hình hệ thống.  
   - Sử dụng `pyproject.toml` để quản lý dependencies.

3. **[Thực hiện thí nghiệm](ca://s?q=Explain_experiment_execution)**  
   - Các bước thí nghiệm phải được mô tả trong `experiments.md`.  
   - Kết quả trung gian cần được lưu lại để đối chiếu.

4. **[Đánh giá kết quả](ca://s?q=Explain_result_evaluation)**  
   - So sánh với chuẩn trong `benchmarks.md`.  
   - Báo cáo sai số, độ tin cậy và giới hạn.

5. **[Tài liệu hóa](ca://s?q=Explain_research_documentation)**  
   - Ghi lại toàn bộ quy trình trong `methodology.md`.  
   - Đảm bảo người khác có thể tái lập mà không cần thêm thông tin ngoài repo.

## Công cụ hỗ trợ

- **Version control**: GitHub để quản lý mã nguồn và tài liệu.  
- **Automation**: GitHub Actions trong `.github/` để kiểm tra khả năng tái lập tự động.  
- **Documentation**: [MkDocs](ca://s?q=Explain_mkdocs.yml) để xây dựng trang tài liệu.  
- **Citation**: Sử dụng `CITATION.cff` để chuẩn hóa trích dẫn.

## Liên hệ

- GitHub: [SciOS Repository](https://github.com/hbdatahoang-ux/SciOS)  
- Email: hbdatahoang@gmail.com  

Mọi thắc mắc hoặc đề xuất cải tiến quy trình tái lập vui lòng mở **issue** trên GitHub hoặc liên hệ trực tiếp qua email.

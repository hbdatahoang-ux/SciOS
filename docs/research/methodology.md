# Research Methodology

Tài liệu này mô tả phương pháp nghiên cứu được áp dụng trong dự án **SciOS**, nhằm đảm bảo tính minh bạch, tái lập và chất lượng khoa học.

## Nguyên tắc cơ bản

- **[Tính minh bạch](ca://s?q=Explain_transparency_in_research)**: Mọi quy trình, dữ liệu và kết quả đều được công khai trong repository.
- **[Khả năng tái lập](ca://s?q=Explain_reproducibility_in_research)**: Các thí nghiệm phải có hướng dẫn chi tiết để người khác có thể thực hiện lại.
- **[Chuẩn hóa](ca://s?q=Explain_standardization_in_research)**: Sử dụng định dạng và quy trình thống nhất cho dữ liệu, mã nguồn và báo cáo.
- **[Đạo đức nghiên cứu](ca://s?q=Explain_research_ethics)**: Tuân thủ các nguyên tắc đạo đức trong khoa học và công bố.

## Quy trình nghiên cứu

1. **[Đề xuất nghiên cứu](ca://s?q=Explain_research_proposals)**  
   - Viết đề xuất trong thư mục `proposals/` theo mẫu `TEMPLATE.md`.  
   - Đề xuất phải nêu rõ mục tiêu, giả thuyết và phương pháp dự kiến.

2. **[Thiết kế thí nghiệm](ca://s?q=Explain_experiment_design)**  
   - Xác định biến số, dữ liệu đầu vào và tiêu chí đánh giá.  
   - Ghi lại trong `experiments.md`.

3. **[Thu thập dữ liệu](ca://s?q=Explain_data_collection)**  
   - Sử dụng tập dữ liệu trong `datasets.md`.  
   - Đảm bảo dữ liệu được mô tả đầy đủ về nguồn gốc và đặc tính.

4. **[Phân tích & Benchmark](ca://s?q=Explain_benchmarking_in_research)**  
   - So sánh kết quả với chuẩn trong `benchmarks.md`.  
   - Sử dụng công cụ phân tích và trực quan hóa để minh họa.

5. **[Tái lập & Kiểm chứng](ca://s?q=Explain_research_validation)**  
   - Ghi lại quy trình trong `reproducibility.md`.  
   - Yêu cầu ít nhất một nhóm độc lập kiểm chứng kết quả.

6. **[Công bố](ca://s?q=Explain_research_publication_process)**  
   - Viết bài báo trong `papers/`.  
   - Cập nhật trạng thái (draft, submitted, accepted, published).  
   - Liệt kê trong `publications.md`.

## Công cụ hỗ trợ

- **Version control**: GitHub để quản lý mã nguồn và tài liệu.  
- **Documentation**: [MkDocs](ca://s?q=Explain_mkdocs.yml) để xây dựng trang tài liệu.  
- **Citation**: Sử dụng `CITATION.cff` để chuẩn hóa trích dẫn.  
- **Automation**: GitHub Actions trong `.github/` để kiểm tra tính tái lập.

## Liên hệ

- GitHub: [SciOS Repository](https://github.com/hbdatahoang-ux/SciOS)  
- Email: hbdatahoang@gmail.com  

Mọi thắc mắc hoặc đề xuất cải tiến phương pháp vui lòng mở **issue** trên GitHub hoặc liên hệ trực tiếp qua email.

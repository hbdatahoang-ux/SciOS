import sys
import os

# Lấy đường dẫn gốc của dự án (thư mục chứa "scios/")
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Thêm vào sys.path nếu chưa có
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

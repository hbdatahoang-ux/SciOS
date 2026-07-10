# preprocess.py
# Image Preprocessor cho SciOS Cognitive Core

from typing import Dict
from PIL import Image

class ImagePreprocessor:
    """
    ImagePreprocessor chịu trách nhiệm xử lý ảnh sau khi nạp:
    - Resize
    - Normalize
    - Augment (tùy chọn)
    """

    def __init__(self, target_size=(224, 224), normalize=True):
        self.target_size = target_size
        self.normalize = normalize

    def resize(self, img: Image.Image) -> Image.Image:
        """Resize ảnh về kích thước chuẩn."""
        return img.resize(self.target_size)

    def normalize_image(self, img: Image.Image) -> Image.Image:
        """Chuẩn hóa ảnh (ví dụ: scale pixel về [0,1])."""
        if not self.normalize:
            return img
        # Chuyển sang RGB nếu cần
        img = img.convert("RGB")
        # Normalize pixel values
        pixels = ( (p[0]/255.0, p[1]/255.0, p[2]/255.0) for p in img.getdata() )
        # Tạo ảnh mới từ normalized pixels
        norm_img = Image.new("RGB", img.size)
        norm_img.putdata([(int(r*255), int(g*255), int(b*255)) for r,g,b in pixels])
        return norm_img

    def preprocess(self, img: Image.Image) -> Dict:
        """
        Thực hiện toàn bộ pipeline preprocess.
        """
        resized = self.resize(img)
        normalized = self.normalize_image(resized)
        return {"preprocessed_image": normalized}

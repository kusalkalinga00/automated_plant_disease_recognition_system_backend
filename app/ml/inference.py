# app/ml/inference.py
import numpy as np
from PIL import Image


def preprocess_pil(img: Image.Image, img_size: tuple[int, int]):
    img = img.convert("RGB").resize(img_size)
    x = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(x, 0)


def topk_indices(probs, k=5):
    import numpy as np

    return np.argsort(probs)[::-1][: min(k, len(probs))].tolist()

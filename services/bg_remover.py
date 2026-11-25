import io
import cv2
import numpy as np
from PIL import Image, ImageFilter

def remove_background(image_bytes: bytes) -> bytes:
    """
    Rasmning orqa fonini aniqlab, uni olib tashlaydi va 
    shaffof (transparent PNG) tasvir qaytaradi.
    """
    # Baytlardan numpy arrayga o'tkazish
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Rasmni ochib bo'lmadi")

    h, w = img.shape[:2]
    
    # Katta rasmlarni tez ishlash uchun masshtablash
    max_dim = 1000
    scale = 1.0
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img_small = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    else:
        img_small = img.copy()

    sh, sw = img_small.shape[:2]

    # GrabCut uchun boshlang'ich maska va modellar
    mask = np.zeros((sh, sw), np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    # Obyekt markazda joylashgan deb hisoblab, to'rtburchak tanlash
    margin_x = max(10, int(sw * 0.05))
    margin_y = max(10, int(sh * 0.05))
    rect = (margin_x, margin_y, sw - 2 * margin_x, sh - 2 * margin_y)

    # 4 marta iteratsiya bilan orqa fonni ajratish
    cv2.grabCut(img_small, mask, rect, bgdModel, fgdModel, 4, cv2.GC_INIT_WITH_RECT)

    # Aniq va ehtimoliy old fon piksellarini ajratish
    mask2 = np.where((mask == 2) | (mask == 0), 0, 255).astype('uint8')

    # Asl o'lchamga qaytarish
    if scale != 1.0:
        mask2 = cv2.resize(mask2, (w, h), interpolation=cv2.INTER_LINEAR)

    # Chetlarni yumshatish (anti-aliasing / feathering)
    mask_pil = Image.fromarray(mask2).filter(ImageFilter.GaussianBlur(1.5))
    mask_smooth = np.array(mask_pil)

    # RGBA formatiga o'tkazish
    b, g, r = cv2.split(img)
    rgba = cv2.merge([b, g, r, mask_smooth])

    # PNG formatida saqlash
    is_success, buffer = cv2.imencode(".png", rgba)
    if not is_success:
        raise ValueError("PNG tasvirga aylantirib bo'lmadi")

    return buffer.tobytes()


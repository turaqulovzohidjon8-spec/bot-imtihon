import os
import math
from io import BytesIO
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

def get_font(size: int, bold: bool = True):
    font_names = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/impact.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for font_path in font_names:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_star(draw: ImageDraw.Draw, cx: float, cy: float, r_out: float, r_in: float, fill_color: tuple):
    """5 qirrali oltin yulduzni aniq geometrik chizish"""
    points = []
    for i in range(10):
        angle = i * math.pi / 5 - math.pi / 2
        r = r_out if i % 2 == 0 else r_in
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=fill_color)

def draw_uzb_flag(draw: ImageDraw.Draw, box: tuple):
    """O'zbekiston bayrog'ini chizish"""
    x1, y1, x2, y2 = box
    h = y2 - y1
    stripe_h = h / 3.0
    
    draw.rectangle([x1, y1, x2, y1 + stripe_h], fill=(0, 153, 229))
    draw.rectangle([x1, y1 + stripe_h, x2, y1 + 2 * stripe_h], fill=(255, 255, 255))
    draw.rectangle([x1, y1 + 2 * stripe_h, x2, y2], fill=(30, 181, 64))
    
    draw.rectangle([x1, y1 + stripe_h - 1, x2, y1 + stripe_h + 1], fill=(216, 30, 5))
    draw.rectangle([x1, y1 + 2 * stripe_h - 1, x2, y1 + 2 * stripe_h + 1], fill=(216, 30, 5))
    
    c_y = y1 + stripe_h * 0.5
    draw.ellipse([x1 + 6, c_y - 5, x1 + 16, c_y + 5], fill=(255, 255, 255))
    draw.ellipse([x1 + 9, c_y - 5, x1 + 19, c_y + 5], fill=(0, 153, 229))
    draw.rectangle([x1, y1, x2, y2], outline=(200, 205, 215), width=1)

def generate_dls_shield_points(w=600, h=750, inset=0):
    """
    Haqiqiy DLS karta qalqoni geometriyasi:
    - Yuqori mayin arka va yumaloq burchaklar
    - To'g'ri vertikal yon chiziqlar
    - Pastki markazga yo'naltirilgan silliq shevron uchi
    """
    xl = 40 + inset
    xr = w - 40 - inset
    xc = w / 2.0
    
    y_corner_top = 70 + inset
    y_side_end = 585 - int(inset * 0.4)
    y_tip = h - 35 - inset
    r_top = max(15, 35 - int(inset * 0.3))
    r_bot = max(12, 28 - int(inset * 0.3))
    
    points = []
    
    # 1. Yuqori arka
    x_arch_l = xl + r_top
    x_arch_r = xr - r_top
    y_arch_base = y_corner_top - 5
    
    for t in np.linspace(0, 1, 30):
        x = x_arch_l * (1 - t) + x_arch_r * t
        elevation = 26 * 4 * t * (1 - t)
        y = y_arch_base - elevation
        points.append((x, y))
        
    # 2. Yuqori o'ng burchak
    cx_tr = xr - r_top
    cy_tr = y_corner_top + 15
    for angle in np.linspace(-math.pi/2, 0, 15):
        x = cx_tr + r_top * math.cos(angle)
        y = cy_tr + (r_top - 15) * math.sin(angle)
        points.append((x, y))
        
    # 3. O'ng to'g'ri vertikal qirra
    points.append((xr, y_side_end))
    
    # 4. Pastki o'ng burilish
    cx_br = xr - r_bot
    cy_br = y_side_end
    for angle in np.linspace(0, math.pi/4, 10):
        x = cx_br + r_bot * math.cos(angle)
        y = cy_br + r_bot * math.sin(angle)
        points.append((x, y))
        
    # 5. Pastki o'ng diagonal -> markaz uchi
    p_diag_r_end = points[-1]
    for t in np.linspace(0, 1, 20):
        x = p_diag_r_end[0] * (1 - t) + xc * t
        y = p_diag_r_end[1] * (1 - t) + y_tip * t
        points.append((x, y))
        
    # 6. Markaz uchidan pastki chap diagonalga
    p_diag_l_start = (xl + r_bot * (1 - math.cos(math.pi/4)), y_side_end + r_bot * math.sin(math.pi/4))
    for t in np.linspace(0, 1, 20):
        x = xc * (1 - t) + p_diag_l_start[0] * t
        y = y_tip * (1 - t) + p_diag_l_start[1] * t
        points.append((x, y))
        
    # 7. Pastki chap burilish
    cx_bl = xl + r_bot
    cy_bl = y_side_end
    for angle in np.linspace(3*math.pi/4, math.pi, 10):
        x = cx_bl + r_bot * math.cos(angle)
        y = cy_bl + r_bot * math.sin(angle)
        points.append((x, y))
        
    # 8. Chap to'g'ri vertikal qirra
    points.append((xl, y_corner_top + 15))
    
    # 9. Yuqori chap burchak
    cx_tl = xl + r_top
    cy_tl = y_corner_top + 15
    for angle in np.linspace(math.pi, 3*math.pi/2, 15):
        x = cx_tl + r_top * math.cos(angle)
        y = cy_tl + (r_top - 15) * math.sin(angle)
        points.append((x, y))
        
    return points

def get_theme_colors(theme: str):
    """14 xil DLS kartasi ranglar palitrasi va hoshiyasi"""
    t = theme.lower().strip()
    themes = {
        "black": {
            "top": (48, 52, 62), "mid": (25, 28, 35), "bot": (12, 14, 18),
            "frame_out": (255, 235, 160), "frame_groove": (45, 38, 25), "frame_main": (225, 185, 75),
            "name": "BLACK CARBON"
        },
        "gold": {
            "top": (255, 225, 90), "mid": (218, 165, 32), "bot": (145, 95, 12),
            "frame_out": (255, 245, 180), "frame_groove": (100, 75, 20), "frame_main": (255, 215, 60),
            "name": "GOLD LEGENDARY"
        },
        "blue": {
            "top": (59, 130, 246), "mid": (29, 78, 216), "bot": (18, 48, 135),
            "frame_out": (210, 235, 255), "frame_groove": (15, 40, 95), "frame_main": (96, 165, 250),
            "name": "RARE BLUE"
        },
        "bronze": {
            "top": (225, 140, 50), "mid": (175, 90, 25), "bot": (115, 60, 18),
            "frame_out": (254, 225, 180), "frame_groove": (80, 40, 12), "frame_main": (215, 145, 85),
            "name": "COMMON BRONZE"
        },
        "sunset": {
            "top": (245, 70, 95), "mid": (249, 120, 25), "bot": (105, 50, 190),
            "frame_out": (255, 240, 170), "frame_groove": (70, 20, 50), "frame_main": (251, 191, 36),
            "name": "SUNSET SPECIAL"
        },
        "purple": {
            "top": (195, 135, 255), "mid": (150, 55, 240), "bot": (90, 30, 140),
            "frame_out": (245, 230, 255), "frame_groove": (60, 20, 90), "frame_main": (192, 132, 252),
            "name": "PURPLE NEON"
        },
        "neon": {
            "top": (235, 125, 250), "mid": (195, 40, 215), "bot": (115, 28, 120),
            "frame_out": (255, 235, 255), "frame_groove": (75, 15, 80), "frame_main": (244, 114, 182),
            "name": "CYBER WAVE"
        },
        "red": {
            "top": (245, 75, 75), "mid": (190, 30, 30), "bot": (130, 25, 25),
            "frame_out": (254, 215, 215), "frame_groove": (80, 15, 15), "frame_main": (248, 113, 113),
            "name": "RED INFERNO"
        },
        "magenta": {
            "top": (248, 118, 185), "mid": (225, 45, 125), "bot": (135, 25, 70),
            "frame_out": (255, 235, 248), "frame_groove": (80, 15, 45), "frame_main": (244, 114, 182),
            "name": "MAGENTA FUSION"
        },
        "orange": {
            "top": (255, 155, 65), "mid": (238, 95, 15), "bot": (160, 55, 20),
            "frame_out": (255, 230, 185), "frame_groove": (90, 35, 10), "frame_main": (251, 146, 60),
            "name": "ORANGE HONEYCOMB"
        },
        "cyan": {
            "top": (45, 215, 245), "mid": (8, 155, 170), "bot": (15, 85, 105),
            "frame_out": (220, 252, 255), "frame_groove": (10, 50, 60), "frame_main": (56, 189, 248),
            "name": "ICE CYAN"
        },
        "classic_gold": {
            "top": (255, 210, 30), "mid": (210, 145, 10), "bot": (140, 85, 15),
            "frame_out": (255, 245, 170), "frame_groove": (90, 60, 15), "frame_main": (250, 204, 21),
            "name": "CLASSIC GOLD"
        },
        "green": {
            "top": (80, 225, 135), "mid": (25, 170, 80), "bot": (22, 90, 50),
            "frame_out": (210, 255, 225), "frame_groove": (12, 60, 30), "frame_main": (74, 222, 128),
            "name": "EMERALD GREEN"
        },
        "world": {
            "top": (175, 110, 15), "mid": (50, 55, 65), "bot": (25, 28, 35),
            "frame_out": (255, 235, 140), "frame_groove": (40, 35, 20), "frame_main": (217, 119, 6),
            "name": "WORLD STARS"
        }
    }
    return themes.get(t, themes["black"])

def create_dls_card(
    player_name: str,
    rating: int = 85,
    position: str = "ST",
    user_photo_bytes: bytes = None,
    stats: dict = None,
    theme: str = "black"
) -> BytesIO:
    """
    Casillas rasmidagi 100% haqiqiy DLS karta generatori
    """
    w, h = 600, 750

    # 1. Tashqi stadium foni (14, 18, 26) - Telegramda aslo oq bo'lmaydi
    card = Image.new("RGB", (w, h), (14, 18, 26))

    palette = get_theme_colors(theme)

    # 2. Qalqon qatlamlari
    outer_points = generate_dls_shield_points(w, h, inset=0)
    frame_mid_points = generate_dls_shield_points(w, h, inset=8)
    frame_bevel_points = generate_dls_shield_points(w, h, inset=14)
    inner_points = generate_dls_shield_points(w, h, inset=26)

    inner_mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(inner_mask).polygon(inner_points, fill=255)

    # 3. 3D Metallik Hoshiya
    draw = ImageDraw.Draw(card)
    # Tashqi ingichka yaltiroq chegara
    draw.polygon(outer_points, fill=palette["frame_out"])
    # Qoramtir relyef o'yig'i
    draw.polygon(frame_mid_points, fill=palette["frame_groove"])
    # Asosiy metallik qavariq hoshiya
    draw.polygon(frame_bevel_points, fill=palette["frame_main"])

    # 4. Ichki gradient va DLS teksturasi
    bg = Image.new("RGB", (w, h), (0, 0, 0))
    bg_draw = ImageDraw.Draw(bg)

    c_top = palette["top"]
    c_mid = palette["mid"]
    c_bot = palette["bot"]

    for y in range(h):
        ratio = y / h
        if ratio < 0.45:
            rel = ratio / 0.45
            r = int(c_top[0] * (1 - rel) + c_mid[0] * rel)
            g = int(c_top[1] * (1 - rel) + c_mid[1] * rel)
            b = int(c_top[2] * (1 - rel) + c_mid[2] * rel)
        else:
            rel = (ratio - 0.45) / 0.55
            r = int(c_mid[0] * (1 - rel) + c_bot[0] * rel)
            g = int(c_mid[1] * (1 - rel) + c_bot[1] * rel)
            b = int(c_mid[2] * (1 - rel) + c_bot[2] * rel)
        bg_draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Carbon fiber yoki nozik to'r naqshi
    for cy in range(0, h, 8):
        for cx in range(0, w, 8):
            bg_draw.point((cx, cy), fill=(c_mid[0] + 15, c_mid[1] + 15, c_mid[2] + 15))

    # DLS takrorlanuvchi nozik suv belgisi
    font_wm = get_font(20, bold=True)
    wm_color = (min(255, c_mid[0] + 25), min(255, c_mid[1] + 25), min(255, c_mid[2] + 25))
    for ry, y in enumerate(range(80, h - 220, 42)):
        off = (ry % 2) * 55
        for x in range(-20, w + 40, 110):
            bg_draw.text((x + off, y), "DLS", fill=wm_color, font=font_wm)

    card.paste(bg, (0, 0), mask=inner_mask)

    # 5. O'YINCHI RASMI
    pw, ph = 340, 390
    px = (w - pw) // 2 + 10
    py = 75

    user_img = None
    if user_photo_bytes and len(user_photo_bytes) > 100:
        try:
            raw_img = Image.open(BytesIO(user_photo_bytes))
            user_img = ImageOps.fit(raw_img, (pw, ph), Image.Resampling.LANCZOS, centering=(0.5, 0.2))
            if user_img.mode != "RGBA":
                user_img = user_img.convert("RGBA")
        except Exception:
            user_img = None

    if user_img is None:
        # Standart sportchi silueti
        user_img = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        u_draw = ImageDraw.Draw(user_img)
        u_draw.ellipse([(pw//2 - 60, 40), (pw//2 + 60, 175)], fill=(225, 230, 240, 255))
        u_draw.polygon([
            (pw//2 - 135, ph),
            (pw//2 - 85, 195),
            (pw//2 + 85, 195),
            (pw//2 + 135, ph)
        ], fill=(225, 230, 240, 255))

    # Rasmni pastki qismini lenta ostiga mayin o'tkazish
    alpha_mask = user_img.split()[3]
    fade_mask = Image.new("L", (pw, ph), 255)
    for fy in range(ph - 75, ph):
        grad_val = int(255 * (1 - (fy - (ph - 75)) / 75))
        ImageDraw.Draw(fade_mask).line([(0, fy), (pw, fy)], fill=grad_val)

    p_mask = Image.composite(fade_mask, Image.new("L", (pw, ph), 0), alpha_mask)

    p_full = Image.new("RGB", (w, h), (0, 0, 0))
    p_full.paste(user_img.convert("RGB"), (px, py))
    p_full_mask = Image.new("L", (w, h), 0)
    p_full_mask.paste(p_mask, (px, py))
    p_final = Image.composite(p_full_mask, Image.new("L", (w, h), 0), inner_mask)
    card.paste(p_full, (0, 0), mask=p_final)

    # 6. METALLIK KULRANG ISM LENTASI (y=475 to y=555)
    ry1, ry2 = 475, 555
    ribbon = Image.new("RGB", (w, h), (0, 0, 0))
    r_draw = ImageDraw.Draw(ribbon)
    for y in range(ry1, ry2):
        rel = (y - ry1) / (ry2 - ry1)
        gr = int(122 - rel * 52)
        r_draw.line([(0, y), (w, y)], fill=(gr, gr + 3, gr + 8))
    r_draw.line([(0, ry1), (w, ry1)], fill=(218, 222, 232), width=2)
    r_draw.line([(0, ry2), (w, ry2)], fill=(32, 35, 42), width=2)

    r_mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(r_mask).rectangle([(0, ry1), (w, ry2)], fill=255)
    r_final = Image.composite(r_mask, Image.new("L", (w, h), 0), inner_mask)
    card.paste(ribbon, (0, 0), mask=r_final)

    draw = ImageDraw.Draw(card)

    # Ism yozuvi
    font_name = get_font(42, bold=True)
    display_name = player_name.upper().strip()[:14]
    n_box = font_name.getbbox(display_name)
    nw = n_box[2] - n_box[0]
    nh = n_box[3] - n_box[1]
    draw.text(((w - nw) // 2, ry1 + (ry2 - ry1 - nh) // 2 - 4), display_name, fill=(255, 255, 255), font=font_name)

    # 7. CHAP YUQORIDAGI DOIRAVIY REYTING BADGE (Yashil doira, oq son)
    cx, cy, cr = 135, 155, 50
    # Oltin xalqasi
    draw.ellipse([(cx - cr - 4, cy - cr - 4), (cx + cr + 4, cy + cr + 4)], fill=(165, 140, 65), outline=(245, 230, 150), width=3)
    # Yashil doira
    draw.ellipse([(cx - cr, cy - cr), (cx + cr, cy + cr)], fill=(22, 195, 60))
    font_rate = get_font(52, bold=True)
    rate_str = str(rating)
    rw_box = font_rate.getbbox(rate_str)
    rw = rw_box[2] - rw_box[0]
    rh = rw_box[3] - rw_box[1]
    draw.text((cx - rw // 2, cy - rh // 2 - 4), rate_str, fill=(255, 255, 255), font=font_rate)

    # 8. YIL KAPSULASI (2025)
    draw.rounded_rectangle([(88, 235), (182, 278)], radius=4, fill=(15, 18, 25), outline=(35, 40, 50), width=2)
    font_year = get_font(26, bold=True)
    year_text = "2025"
    yw_box = font_year.getbbox(year_text)
    yw = yw_box[2] - yw_box[0]
    draw.text((88 + (94 - yw) // 2, 241), year_text, fill=(255, 222, 75), font=font_year)

    # 9. LENTA OSTIDAGI NISHONLAR (BAYROQ VA POZITSIYA)
    my = 572
    flag_w, pos_w, bh = 66, 66, 36
    tot = flag_w + pos_w + 12
    sx = (w - tot) // 2

    # O'zbekiston bayrog'i
    draw_uzb_flag(draw, (sx, my, sx + flag_w, my + bh))

    # Pozitsiya nishoni (ST, GK, CAM va h.k.)
    pos_box = [(sx + flag_w + 12, my), (sx + flag_w + 12 + pos_w, my + bh)]
    draw.rounded_rectangle(pos_box, radius=4, fill=(14, 165, 233), outline=(10, 130, 200), width=1)
    font_pos = get_font(24, bold=True)
    pos_text = position.upper()
    pw_box = font_pos.getbbox(pos_text)
    pw = pw_box[2] - pw_box[0]
    draw.text((pos_box[0][0] + (pos_w - pw) // 2, my + 4), pos_text, fill=(255, 255, 255), font=font_pos)

    # 10. PASTKI SHEVRON UCHIDA: 5 QIRRALI OLTIN YULDUZ
    draw_star(draw, w // 2, 648, r_out=22, r_in=9, fill_color=(250, 204, 21))

    output = BytesIO()
    card.save(output, format="PNG")
    output.seek(0)
    return output

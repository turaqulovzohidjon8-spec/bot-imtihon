import os
import math
import random
import wave
import subprocess
from io import BytesIO
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import imageio_ffmpeg
from config import OUTPUT_DIR

def get_font(size: int, bold: bool = False):
    font_names = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for font_path in font_names:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def synthesize_audio(occasion_type: str, duration_sec: float, output_wav_path: str):
    """
    Bayram turiga mos ravishda real musiqiy ohang (WAV) generatsiya qilish
    """
    sr = 44100
    total_samples = int(sr * duration_sec)
    audio = np.zeros(total_samples, dtype=np.float32)

    def note_freq(name: str) -> float:
        freqs = {
            "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23,
            "G4": 392.00, "A4": 440.00, "B4": 493.88, "C5": 523.25,
            "D5": 587.33, "E5": 659.25, "F5": 698.46, "G5": 783.99,
            "A#4": 466.16, "F#4": 369.99
        }
        return freqs.get(name, 440.0)

    def add_tone(start_time, dur, freq, amp=0.25):
        start_idx = int(start_time * sr)
        tone_samples = int(dur * sr)
        if start_idx + tone_samples > total_samples:
            tone_samples = total_samples - start_idx
        if tone_samples <= 0:
            return
        t = np.linspace(0, dur, tone_samples, False)
        envelope = np.exp(-3.5 * (t / dur))
        wave_val = (
            np.sin(2 * np.pi * freq * t) * 0.6 +
            np.sin(2 * np.pi * freq * 2.0 * t) * 0.25 +
            np.sin(2 * np.pi * freq * 3.0 * t) * 0.15
        ) * envelope * amp
        audio[start_idx:start_idx + tone_samples] += wave_val

    if occasion_type == "Tug'ilgan kun":
        melody = [
            ("C4", 0.35), ("C4", 0.35), ("D4", 0.7), ("C4", 0.7), ("F4", 0.7), ("E4", 1.2),
            ("C4", 0.35), ("C4", 0.35), ("D4", 0.7), ("C4", 0.7), ("G4", 0.7), ("F4", 1.2)
        ]
        cur = 0.2
        for n, d in melody:
            add_tone(cur, d, note_freq(n), amp=0.35)
            add_tone(cur, d * 1.5, note_freq(n) / 2.0, amp=0.15)
            cur += d * 0.85
    else:
        chords = [
            ["D4", "F#4", "A4", "D5"],
            ["G4", "B4", "D5", "G5"],
            ["A4", "C#5", "E5", "A5"],
            ["D4", "F#4", "A4", "D5"]
        ]
        cur = 0.2
        for chord in chords:
            for note in chord:
                add_tone(cur, 0.5, note_freq(note), amp=0.3)
                cur += 0.25
            cur += 0.3

    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.85

    audio_int16 = (audio * 32767).astype(np.int16)
    with wave.open(output_wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())

def generate_greeting_video(
    recipient_name: str,
    occasion_type: str = "Tug'ilgan kun",
    custom_wish: str = None,
    recipient_photo_bytes: bytes = None
) -> str:
    """
    Ovozli, animatsion va ixtiyoriy rasm bilan boyitilgan tabrik videoroligi (MP4)
    """
    width, height = 720, 1280
    fps = 24
    duration_sec = 6.0
    total_frames = int(fps * duration_sec)
    
    rnd_id = random.randint(10000, 99999)
    temp_video_path = str(OUTPUT_DIR / f"temp_v_{rnd_id}.mp4")
    temp_audio_path = str(OUTPUT_DIR / f"temp_a_{rnd_id}.wav")
    final_output_path = str(OUTPUT_DIR / f"tabrik_{rnd_id}.mp4")

    synthesize_audio(occasion_type, duration_sec, temp_audio_path)

    default_wishes = {
        "Tug'ilgan kun": "Tavallud ayyomingiz qutlug' bo'lsin! Baxt, salomatlik va cheksiz omad tilayman!",
        "To'y": "Nikoh to'yingiz muborak bo'lsin! Mustahkam va baxtli oila bo'lib yashang!",
        "Yangi Yil": "Yangi yil xonadoningizga tinchlik, fayz va qut-baraka olib kelsin!",
        "8-Mart": "Xalqaro xotin-qizlar kuni muborak bo'lsin! Bahoriy go'zallik tark etmasin!",
        "Hayit": "Ulug' ayyom muborak bo'lsin! Ezgu niyatlaringiz ijobat bo'lsin!",
        "Umumiy": "Barcha yaxshi tilaklar sizga hamroh bo'lsin! Yuzingizdan kulgu arimasin!"
    }
    wish_text = custom_wish or default_wishes.get(occasion_type, default_wishes["Umumiy"])

    if occasion_type == "Tug'ilgan kun":
        bg_color_top = (15, 23, 42)
        bg_color_bot = (88, 28, 135)
        accent_color = (255, 215, 0)
    elif occasion_type == "To'y":
        bg_color_top = (68, 8, 30)
        bg_color_bot = (136, 19, 55)
        accent_color = (255, 230, 180)
    elif occasion_type == "8-Mart":
        bg_color_top = (131, 24, 67)
        bg_color_bot = (190, 24, 93)
        accent_color = (254, 240, 138)
    else:
        bg_color_top = (17, 24, 39)
        bg_color_bot = (6, 78, 59)
        accent_color = (250, 204, 21)

    bg_img = Image.new("RGB", (width, height))
    draw_bg = ImageDraw.Draw(bg_img)
    for y in range(height):
        ratio = y / height
        r = int(bg_color_top[0] * (1 - ratio) + bg_color_bot[0] * ratio)
        g = int(bg_color_top[1] * (1 - ratio) + bg_color_bot[1] * ratio)
        b = int(bg_color_top[2] * (1 - ratio) + bg_color_bot[2] * ratio)
        draw_bg.line([(0, y), (width, y)], fill=(r, g, b))

    # O'yinchi/tabrik egasi rasmini tayyorlash
    has_photo = False
    photo_cropped = None
    if recipient_photo_bytes:
        try:
            p_img = Image.open(BytesIO(recipient_photo_bytes)).convert("RGBA")
            p_size = 280
            p_img = ImageOps.fit(p_img, (p_size, p_size), Image.Resampling.LANCZOS)
            # Dumaloq maska
            p_mask = Image.new("L", (p_size, p_size), 0)
            ImageDraw.Draw(p_mask).ellipse([(0, 0), (p_size, p_size)], fill=255)
            
            p_canvas = Image.new("RGBA", (p_size, p_size), (0, 0, 0, 0))
            p_canvas.paste(p_img, (0, 0), mask=p_mask)
            photo_cropped = p_canvas
            has_photo = True
        except Exception:
            has_photo = False

    particles = []
    for _ in range(85):
        particles.append({
            "x": random.randint(0, width),
            "y": random.randint(-height, height),
            "speed": random.uniform(3, 8),
            "size": random.randint(3, 8),
            "color": random.choice([
                (255, 215, 0), (255, 255, 255), (255, 182, 193), 
                (255, 105, 180), (135, 206, 250), (255, 223, 0)
            ]),
            "angle": random.uniform(0, 2 * math.pi)
        })

    font_badge = get_font(36, bold=True)
    font_name = get_font(60 if has_photo else 68, bold=True)
    font_wish = get_font(32 if has_photo else 34, bold=False)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))

    try:
        for frame_idx in range(total_frames):
            frame_img = bg_img.copy()
            draw = ImageDraw.Draw(frame_img, "RGBA")

            # Zarrachalar harakati
            for p in particles:
                p["y"] += p["speed"]
                p["x"] += math.sin(p["angle"] + frame_idx * 0.1) * 2
                if p["y"] > height:
                    p["y"] = random.randint(-50, -10)
                    p["x"] = random.randint(0, width)
                draw.ellipse(
                    [(p["x"] - p["size"], p["y"] - p["size"]),
                     (p["x"] + p["size"], p["y"] + p["size"])],
                    fill=p["color"] + (220,)
                )

            # Bezakli ramka
            margin = 35
            draw.rounded_rectangle(
                [(margin, margin), (width - margin, height - margin)],
                radius=35,
                outline=accent_color + (180,),
                width=4
            )

            # Badge (Yuqori yozuv)
            badge_y = 130 if has_photo else 220
            badge_text = f"✨ {occasion_type.upper()} MUBORAK! ✨"
            badge_box = font_badge.getbbox(badge_text)
            bw = badge_box[2] - badge_box[0]
            draw.text(((width - bw) // 2, badge_y), badge_text, fill=accent_color + (255,), font=font_badge)

            # Agar rasm bo'lsa, o'rtada nurlangan doirada ko'rsatish
            if has_photo and photo_cropped:
                p_center_y = 350
                p_box_x = (width - 280) // 2
                p_box_y = p_center_y - 140
                
                # Porlash halqasi
                pulse = int(10 * math.sin(frame_idx * 0.2))
                glow_box = [(p_box_x - 12 - pulse, p_box_y - 12 - pulse), (p_box_x + 280 + 12 + pulse, p_box_y + 280 + 12 + pulse)]
                draw.ellipse(glow_box, fill=accent_color + (80,))
                
                # Oltin ramka
                frame_img.paste(photo_cropped, (p_box_x, p_box_y), mask=photo_cropped)
                draw.ellipse([(p_box_x - 3, p_box_y - 3), (p_box_x + 283, p_box_y + 283)], outline=accent_color + (255,), width=6)

            # Ism
            name_y = 530 if has_photo else 440
            name_text = recipient_name.title()
            name_box = font_name.getbbox(name_text)
            nw = name_box[2] - name_box[0]
            draw.text(((width - nw) // 2, name_y), name_text, fill=(255, 255, 255, 255), font=font_name)
            
            sep_y = name_y + 80
            draw.line([(width // 2 - 160, sep_y), (width // 2 + 160, sep_y)], fill=accent_color + (220,), width=3)

            # Matn
            words = wish_text.split()
            lines = []
            curr_line = ""
            for word in words:
                test_line = f"{curr_line} {word}".strip()
                bbox = font_wish.getbbox(test_line)
                if (bbox[2] - bbox[0]) < (width - 160):
                    curr_line = test_line
                else:
                    lines.append(curr_line)
                    curr_line = word
            if curr_line:
                lines.append(curr_line)

            text_y = sep_y + 50
            for line in lines:
                l_box = font_wish.getbbox(line)
                lw = l_box[2] - l_box[0]
                draw.text(((width - lw) // 2, text_y), line, fill=(240, 245, 255, 245), font=font_wish)
                text_y += 50

            footer_text = "🎉 Chin dildan eng ezgu tilaklar! 🎉"
            f_box = font_badge.getbbox(footer_text)
            fw = f_box[2] - f_box[0]
            draw.text(((width - fw) // 2, height - 160), footer_text, fill=accent_color + (220,), font=font_badge)

            np_frame = np.array(frame_img.convert("RGB"))
            bgr_frame = cv2.cvtColor(np_frame, cv2.COLOR_RGB2BGR)
            video_writer.write(bgr_frame)
    finally:
        video_writer.release()

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, "-y",
        "-i", temp_video_path,
        "-i", temp_audio_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        final_output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for tmp in [temp_video_path, temp_audio_path]:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass

    return final_output_path

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'media' / 'flight914-explainer.ko.mp4'
W, H, FPS = 1280, 720, 24
font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
if not Path(font_path).exists():
    import subprocess
    font_path = subprocess.check_output(['fc-match', '-f', '%{file}', 'Noto Sans CJK KR']).decode().strip()
font = ImageFont.truetype(font_path, 27)
small = ImageFont.truetype(font_path, 20)
label_font = ImageFont.truetype(font_path, 18)
scenes = [
    ('assets/images/hero-storm-flight.jpg', 'Flight 914라는 표기는 어디서 왔을까?', '온라인 판본의 제목과 영화 카탈로그의 제목을 구분합니다.'),
    ('assets/images/two-eras-sky.jpg', '현대 여객기가 1940년의 하늘로', '시간 이동 SF와 전쟁 액션이 만나는 이야기의 전제.'),
    ('assets/images/cockpit-at-dusk.jpg', '폭풍, 과거, 제한된 시간', '밀폐된 조종실과 객실이 만드는 독립 리뷰의 감상 포인트.'),
]

def fit_zoom(img, t):
    # A gentle editorial push-in; use only the independently generated art.
    scale = 1.0 + 0.055 * t
    sw, sh = int(W * scale), int(H * scale)
    resized = ImageOps.fit(img, (sw, sh), method=Image.Resampling.LANCZOS)
    x = int((sw - W) * (0.35 + 0.3 * t))
    y = int((sh - H) * (0.35 + 0.3 * (1-t)))
    return resized.crop((x, y, x+W, y+H)).convert('RGBA')

def draw_card(base, label, title, desc, disclaimer=False):
    overlay = Image.new('RGBA', (W, H), (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    # Top-left site tag
    d.rounded_rectangle((48, 38, 340, 82), radius=18, fill=(5,16,25,200), outline=(243,180,92,220), width=2)
    d.text((66, 48), 'FLIGHT 914  ·  독립 영화 리뷰', font=label_font, fill=(255,239,208,255))
    # Bottom fade, solid translucent band
    d.rectangle((0, H-226, W, H), fill=(3,11,17,208))
    d.text((58, H-206), label, font=small, fill=(243,180,92,255))
    d.text((58, H-166), title, font=font, fill=(255,255,255,255), stroke_width=1, stroke_fill=(0,0,0,120))
    d.text((58, H-108), desc, font=small, fill=(218,231,234,255))
    if disclaimer:
        d.rounded_rectangle((58, H-57, W-58, H-20), radius=12, fill=(8,20,29,230), outline=(115,212,212,200), width=1)
        d.text((75, H-51), '창작 콘셉트 아트 · 실제 영화 장면이나 공식 홍보물이 아닙니다', font=label_font, fill=(223,249,245,255))
    return Image.alpha_composite(base, overlay).convert('RGB')

imgs = [Image.open(ROOT / p).convert('RGB') for p,_,_ in scenes]
writer = imageio_ffmpeg.write_frames(
    str(OUT), (W,H), fps=FPS, codec='libx264', pix_fmt_in='rgb24', pix_fmt_out='yuv420p',
    quality=8, macro_block_size=16, ffmpeg_log_level='error',
    output_params=['-movflags','+faststart','-an']
)
writer.send(None)
scene_seconds = 6
for i, (img, scene) in enumerate(zip(imgs, scenes)):
    _, title, desc = scene
    for frame_no in range(scene_seconds * FPS):
        t = frame_no / max(1, scene_seconds * FPS - 1)
        frame = fit_zoom(img, t)
        # Fade between panels with a short black dissolve.
        fade = min(1.0, frame_no/(FPS*0.45), (scene_seconds*FPS-1-frame_no)/(FPS*0.45))
        frame = Image.blend(Image.new('RGB',(W,H),(4,12,18)), frame.convert('RGB'), max(0.0,fade))
        frame = draw_card(frame.convert('RGBA'), f'{i+1:02d}  /  03', title, desc, disclaimer=(i==2 and frame_no>FPS*4.2))
        writer.send(np.asarray(frame, dtype=np.uint8).tobytes())
writer.close()
print(OUT, OUT.stat().st_size)

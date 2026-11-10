"""生成心屿 Mindisle 访问二维码（含手机端访问说明）"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / ".venv" / "Lib" / "site-packages"))

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw, ImageFont

URL = "https://vip-expense-wit-additional.trycloudflare.com"
OUT = Path(__file__).parent.parent / "screenshots"
OUT.mkdir(exist_ok=True)

# ---------- 配色（心屿设计系统）----------
SEA = (46, 110, 104)        # #2E6E68 墨绿
SEA_DEEP = (34, 82, 78)     # #22524E
INK = (27, 42, 44)          # #1B2A2C
INK_2 = (86, 105, 109)      # #56696D
INK_3 = (148, 164, 166)     # #94A4A6
LAMP = (217, 152, 47)       # #D9982F 琥珀
BG = (246, 245, 241)        # #F6F5F1 米白
SURFACE = (255, 255, 255)
LINE = (231, 229, 222)


def load_font(size, bold=False):
    """尝试加载中文字体，按优先级回退"""
    candidates = [
        ("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"),
        ("C:/Windows/Fonts/msyhbd.ttf" if bold else "C:/Windows/Fonts/msyh.ttf"),
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ---------- 1. 生成二维码本体 ----------
qr = qrcode.QRCode(
    version=None,
    error_correction=ERROR_CORRECT_H,   # 高容错，中间可放 logo
    box_size=12,
    border=2,
)
qr.add_data(URL)
qr.make(fit=True)

qr_img = qr.make_image(fill_color=SEA_DEEP, back_color=SURFACE).convert("RGB")
qr_size = qr_img.size[0]

# ---------- 2. 排版成一张卡片 ----------
W = 900
PAD = 56
CARD_W = W - PAD * 2

TITLE_H = 106
QR_AREA = qr_size + 48
URL_H = 96
TIP_H = 120
FOOT_H = 54

CARD_H = TITLE_H + QR_AREA + URL_H + TIP_H + FOOT_H
H = CARD_H + PAD * 2

canvas = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(canvas)

# 卡片底
draw.rounded_rectangle(
    [PAD, PAD, PAD + CARD_W, PAD + CARD_H],
    radius=28, fill=SURFACE, outline=LINE, width=2,
)

y = PAD + 40

# --- 标题 ---
f_title = load_font(40, bold=True)
f_eyebrow = load_font(20)
f_sub = load_font(23)
f_url = load_font(25)
f_tip = load_font(22)
f_tip_b = load_font(22, bold=True)
f_foot = load_font(19)

eyebrow = "MINDISLE · 心屿"
draw.text((W // 2, y), eyebrow, font=f_eyebrow, fill=SEA, anchor="ma")
y += 34

draw.text((W // 2, y), "扫码打开 · 心屿心理支持", font=f_title, fill=INK, anchor="ma")
y += 52

draw.text((W // 2, y), "用手机相机或微信扫一扫即可访问", font=f_sub, fill=INK_2, anchor="ma")
y += TITLE_H - 52 - 34 + 26

# --- 二维码 ---
qr_x = (W - qr_size) // 2
qr_y = y

# 二维码外框（浅墨绿底 + 圆角）
pad_box = 20
draw.rounded_rectangle(
    [qr_x - pad_box, qr_y - pad_box, qr_x + qr_size + pad_box, qr_y + qr_size + pad_box],
    radius=20, fill=(226, 239, 236),   # --sea-soft
)
canvas.paste(qr_img, (qr_x, qr_y))

# 中间放个"心"字标记
cx, cy = qr_x + qr_size // 2, qr_y + qr_size // 2
mark_r = 46
draw.ellipse([cx - mark_r, cy - mark_r, cx + mark_r, cy + mark_r], fill=SURFACE, outline=SEA, width=3)
f_mark = load_font(48, bold=True)
draw.text((cx, cy - 4), "心", font=f_mark, fill=SEA_DEEP, anchor="mm")

y = qr_y + qr_size + pad_box + 30

# --- 网址 ---
draw.text((W // 2, y), URL, font=f_url, fill=SEA_DEEP, anchor="ma")
y += 40

# 分隔线
draw.line([(PAD + 90, y), (PAD + CARD_W - 90, y)], fill=LINE, width=1)
y += 26

# --- 提示 ---
draw.text((W // 2, y), "手机需能访问外网（建议用 Wi-Fi 或移动数据）", font=f_tip, fill=INK_3, anchor="ma")
y += 32
draw.text((W // 2, y), "若打不开，请确认电脑端服务与隧道仍在运行", font=f_tip, fill=INK_3, anchor="ma")

# --- 底部 ---
fy = PAD + CARD_H - 46
draw.text((W // 2, fy), "公益心理支持 · 全部咨询免费", font=f_foot, fill=LAMP, anchor="ma")

# ---------- 3. 保存 ----------
png_path = OUT / "扫码访问-心屿.png"
canvas.save(png_path, "PNG", optimize=True)

# 单独存一份纯二维码（方便嵌入 PPT / 文档）
qr_only = OUT / "二维码-心屿.png"
qr_img.save(qr_only, "PNG", optimize=True)

print("生成完成：")
print("  完整卡片:", png_path)
print("  纯二维码:", qr_only)
print("  尺寸:", canvas.size)
print("  网址:", URL)

"""滑块验证码：纯 Pillow 生成，Redis 存正确答案。"""
import base64
import io
import secrets
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFilter

from app.core.redis import get_redis

_BG_W = 320
_BG_H = 160
_PIECE = 50
_TOLERANCE = 6  # 允许 ±6 像素误差

_REDIS_KEY = "captcha:slide:{cid}"
_REDIS_TTL = 300  # 5 分钟


@dataclass
class CaptchaChallenge:
    captcha_id: str
    bg_image_b64: str
    jigsaw_image_b64: str
    jigsaw_y: int  # 拼图块的 Y 坐标（X 固定从 0 开始）


def _rand_bg() -> Image.Image:
    """生成随机彩色渐变背景。"""
    img = Image.new("RGB", (_BG_W, _BG_H))
    pix = img.load()
    r1, g1, b1 = secrets.randbelow(200), secrets.randbelow(200), secrets.randbelow(200)
    r2, g2, b2 = secrets.randbelow(200) + 55, secrets.randbelow(200) + 55, secrets.randbelow(200) + 55
    for x in range(_BG_W):
        for y in range(_BG_H):
            t = (x + y) / (_BG_W + _BG_H)
            r = int(r1 * (1 - t) + r2 * t)
            g = int(g1 * (1 - t) + g2 * t)
            b = int(b1 * (1 - t) + b2 * t)
            pix[x, y] = (r, g, b)
    # 撒一些噪点圆圈，增加视觉特征
    draw = ImageDraw.Draw(img)
    for _ in range(8):
        cx = secrets.randbelow(_BG_W)
        cy = secrets.randbelow(_BG_H)
        rr = secrets.randbelow(25) + 10
        color = (secrets.randbelow(256), secrets.randbelow(256), secrets.randbelow(256))
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=color, width=2)
    return img


def _piece_mask() -> Image.Image:
    """生成拼图块的 alpha 蒙版（简单圆角方形）。"""
    mask = Image.new("L", (_PIECE, _PIECE), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([2, 2, _PIECE - 2, _PIECE - 2], radius=10, fill=255)
    return mask


def generate() -> tuple[CaptchaChallenge, int]:
    """生成一对图：带缺口的背景 + 拼图块。返回 (挑战, 正确 X 坐标)"""
    bg = _rand_bg()

    # 正确位置：靠右随机
    target_x = secrets.randbelow(_BG_W - _PIECE - 80) + 70
    target_y = secrets.randbelow(_BG_H - _PIECE - 20) + 10

    mask = _piece_mask()
    # 从背景上抠出拼图块
    piece_area = (target_x, target_y, target_x + _PIECE, target_y + _PIECE)
    piece_crop = bg.crop(piece_area)
    piece_img = Image.new("RGBA", (_PIECE, _PIECE), (0, 0, 0, 0))
    piece_img.paste(piece_crop, (0, 0), mask)

    # 在背景上把这块画暗，形成缺口
    overlay = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(
        [target_x + 2, target_y + 2, target_x + _PIECE - 2, target_y + _PIECE - 2],
        radius=10,
        fill=(0, 0, 0, 130),
        outline=(255, 255, 255, 200),
        width=2,
    )
    bg_with_hole = Image.alpha_composite(bg.convert("RGBA"), overlay)

    captcha_id = secrets.token_urlsafe(12)

    bg_buf = io.BytesIO()
    bg_with_hole.save(bg_buf, format="PNG", optimize=True)
    piece_buf = io.BytesIO()
    piece_img.save(piece_buf, format="PNG", optimize=True)

    return CaptchaChallenge(
        captcha_id=captcha_id,
        bg_image_b64="data:image/png;base64," + base64.b64encode(bg_buf.getvalue()).decode(),
        jigsaw_image_b64="data:image/png;base64," + base64.b64encode(piece_buf.getvalue()).decode(),
        jigsaw_y=target_y,
    ), target_x


async def store_answer(captcha_id: str, target_x: int) -> None:
    redis = get_redis(required=True)
    await redis.set(_REDIS_KEY.format(cid=captcha_id), str(target_x), ex=_REDIS_TTL)


async def verify(captcha_id: str, slide_x: int) -> bool:
    """校验并立即销毁（一次性使用）。"""
    redis = get_redis(required=True)
    key = _REDIS_KEY.format(cid=captcha_id)
    raw = await redis.get(key)
    if raw is None:
        return False
    await redis.delete(key)
    try:
        target = int(raw)
    except (TypeError, ValueError):
        return False
    return abs(slide_x - target) <= _TOLERANCE


def img_size() -> tuple[int, int, int]:
    return _BG_W, _BG_H, _PIECE

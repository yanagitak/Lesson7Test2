import os
import io
import base64
from flask import Flask, request, render_template
import qrcode
from qrcode.constants import (
    ERROR_CORRECT_L,
    ERROR_CORRECT_M,
    ERROR_CORRECT_Q,
    ERROR_CORRECT_H,
)

app = Flask(__name__)

# デバッグ切替
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# 制限値
MAX_TEXT_LEN = 500
MAX_SIZE = 1024

ERROR_LEVELS = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}


def generate_qr_png_data(text: str, size: int, border: int, level: str) -> str:
    """QRコードを生成し、Data URL（base64 PNG）を返す"""
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_LEVELS[level],
        box_size=10,
        border=border,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((size, size))

    buf = io.BytesIO()
    img.save(buf, format="PNG")

    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


@app.route("/", methods=["GET", "POST"])
def index():
    error = ""
    img_data = ""

    # デフォルト値
    text = ""
    size = 300
    border = 4
    level = "M"

    if request.method == "POST":
        try:
            text = request.form.get("text", "").strip()
            size = int(request.form.get("size", size))
            border = int(request.form.get("border", border))
            level = request.form.get("level", level)

            if not text:
                raise ValueError("テキストを入力してください。")
            if len(text) > MAX_TEXT_LEN:
                raise ValueError(f"テキストは最大 {MAX_TEXT_LEN} 文字までです。")
            if size <= 0 or size > MAX_SIZE:
                raise ValueError(f"サイズは 1〜{MAX_SIZE}px の範囲で指定してください。")
            if border < 0 or border > 10:
                raise ValueError("余白（border）は 0〜10 の範囲で指定してください。")
            if level not in ERROR_LEVELS:
                raise ValueError("誤り訂正レベルが不正です。")

            img_data = generate_qr_png_data(text, size, border, level)

        except Exception as e:
            error = str(e)

    return render_template(
        "index.html", # ここで渡す先のhtmlファイルを指定する
        text=text,
        size=size,
        border=border,
        level=level,
        img_data=img_data,
        error=error,
        max_text_len=MAX_TEXT_LEN,
        max_size=MAX_SIZE,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=DEBUG)

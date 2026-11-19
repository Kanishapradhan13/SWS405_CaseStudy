from PIL import Image, ImageDraw, ImageFont
F = "/System/Library/Fonts/Menlo.ttc"
def render(lines, path, title="Terminal", w=1400, fs=19, upto=None):
    font = ImageFont.truetype(F, fs); bold = ImageFont.truetype(F, fs, index=1)
    lh = fs + 7; h = 52 + lh * (len(lines) if upto is None else upto) + 24
    im = Image.new("RGB", (w, max(h, 160)), "#1e1e1e"); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, 36], fill="#3a3a3a")
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]): d.ellipse([14 + i * 24, 11, 28 + i * 24, 25], fill=c)
    d.text((w // 2 - 80, 8), title, fill="#bbbbbb", font=ImageFont.truetype(F, 15))
    y = 50
    for ln in (lines if upto is None else lines[:upto]):
        col = "#d4d4d4"
        if ln.startswith("$ "): col = "#7ee787"
        elif "MATCH" in ln or "OK" == ln.strip()[-2:]: col = "#79c0ff"
        elif "REJECTED" in ln: col = "#ff7b72"
        d.text((18, y), ln[:int((w - 36) / (fs * 0.6))], fill=col, font=bold if ln.startswith("$ ") else font); y += lh
    im.save(path)

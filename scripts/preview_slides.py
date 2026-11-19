import sys
from pptx import Presentation
from pptx.util import Emu
from PIL import Image, ImageDraw, ImageFont
PX = 100  # px per inch
FR = "/System/Library/Fonts/Supplemental/Arial.ttf"; FB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
def font(sz, b=False): return ImageFont.truetype(FB if b else FR, int(round(sz * PX / 72)))
def inch(v): return v / 914400 * PX
def wrap(d, text, f, maxw):
    out = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split(" "):
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= maxw or not cur: cur = t
            else: out.append(cur); cur = w
        out.append(cur)
    return out
issues = []
def draw_text(d, tf, x, y, w, h, tag, default_color="#000000", pad=5):
    cy = y + 3; first = True
    for p in tf.paragraphs:
        runs = p.runs
        if not runs: continue
        r = runs[0]; sz = r.font.size.pt if r.font.size else 18; b = bool(r.font.bold)
        try: col = "#" + str(r.font.color.rgb)
        except Exception: col = default_color
        f = font(sz, b); text = "".join(x.text for x in runs)
        pPr = p._p.pPr; bullet = pPr is not None and pPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}buChar") is not None
        indent = inch(228600) if bullet else 0
        lines = wrap(d, text, f, w - 2 * pad - indent)
        lh = sz * PX / 72 * 1.2
        for ln in lines:
            if bullet and ln is lines[0]: d.text((x + pad, cy), "•", font=f, fill=col)
            d.text((x + pad + indent, cy), ln, font=f, fill=col)
            if p.alignment is not None and int(p.alignment) == 2:  # center
                pass
            cy += lh
        cy += (p.space_after.pt * PX / 72) if p.space_after else 0
    if cy - 3 > y + h + 2: issues.append(f"{tag}: text overflows box by {round((cy-3-(y+h))/PX,2)} in")
def render(path, outdir):
    prs = Presentation(path)
    for n, s in enumerate(prs.slides, 1):
        im = Image.new("RGB", (int(13.333 * PX), int(7.5 * PX)), "white"); d = ImageDraw.Draw(im)
        title_layout = s.slide_layout.name == "Title Slide"
        if title_layout:
            d.rectangle([0, 0, im.width, im.height], fill="#005493"); d.rectangle([12, 0, 327, 750], fill="#0F6FC6")
            for sh in s.slide_layout.shapes:
                if sh.shape_type == 13: im.paste(Image.open(__import__("io").BytesIO(sh.image.blob)).convert("RGB").resize((int(inch(sh.width)), int(inch(sh.height)))), (int(inch(sh.left)), int(inch(sh.top))))
        else:
            d.rectangle([0, 0, im.width, 79], fill="#125463"); d.rectangle([0, 695, im.width, 750], fill="#125463")
            d.text((20, 22), "CST", font=font(22, True), fill="white"); d.text((128, 14), "College of Science and Technology\nRoyal University of Bhutan", font=font(12), fill="white")
            d.text((330, 712), "A centre of excellence in science and technology enriched with GNH values", font=font(12), fill="white")
        for sh in s.shapes:
            x, y, w, h = inch(sh.left), inch(sh.top), inch(sh.width), inch(sh.height)
            tag = f"slide {n} [{sh.name}]"
            if sh.is_placeholder and sh.placeholder_format.type in (1, 3) :
                f = font(28 if not title_layout else 36, not title_layout is False)
                col = "#0432FF" if not title_layout else "#FFFFFF"
                if not title_layout:
                    lines = wrap(d, sh.text_frame.text, font(28), w - 10)
                    if len(lines) > 1: issues.append(f"{tag}: title wraps to {len(lines)} lines")
                    d.text((x + 5, y + 8), sh.text_frame.text, font=font(28), fill=col)
                else:
                    t = sh.text_frame.text; sz = 36
                    d.multiline_text((x + 5, y + 8), "\n".join(wrap(d, t, font(sz, True), w - 10)), font=font(sz, True), fill=col, spacing=8)
                continue
            if sh.is_placeholder and sh.placeholder_format.type == 4:
                d.multiline_text((x + 5, y + 8), sh.text_frame.text, font=font(18), fill="white"); continue
            if sh.shape_type == 13:
                im.paste(Image.open(__import__("io").BytesIO(sh.image.blob)).convert("RGB").resize((int(w), int(h))), (int(x), int(y)))
                if x + w > 13.34 * PX or y + h > 6.9 * PX: issues.append(f"{tag}: picture beyond safe area")
                continue
            if sh.has_table if hasattr(sh, "has_table") else False:
                t = sh.table; cy = y
                for ri, row in enumerate(t.rows):
                    cx = x; rh = row.height / 914400 * PX; need = 0
                    for ci, col in enumerate(t.columns):
                        c = t.cell(ri, ci); cw = col.width / 914400 * PX
                        r0 = c.text_frame.paragraphs[0].runs[0]; f = font(r0.font.size.pt, bool(r0.font.bold))
                        ls = wrap(d, c.text_frame.text, f, cw - 2 * inch(91440)); need = max(need, len(ls) * r0.font.size.pt * PX / 72 * 1.2 + 14)
                    rh = max(rh, need)
                    for ci, col in enumerate(t.columns):
                        c = t.cell(ri, ci); cw = col.width / 914400 * PX
                        fc = "#" + str(c.fill.fore_color.rgb); d.rectangle([cx, cy, cx + cw, cy + rh], fill=fc, outline="#9CA3AF")
                        r0 = c.text_frame.paragraphs[0].runs[0]; f = font(r0.font.size.pt, bool(r0.font.bold)); ls = wrap(d, c.text_frame.text, f, cw - 20)
                        ty = cy + (rh - len(ls) * r0.font.size.pt * PX / 72 * 1.2) / 2
                        for ln in ls: d.text((cx + 10, ty), ln, font=f, fill="#" + str(r0.font.color.rgb)); ty += r0.font.size.pt * PX / 72 * 1.2
                        cx += cw
                    cy += rh
                if cy > 6.9 * PX: issues.append(f"{tag}: table bottom at {round(cy/PX,2)} in (footer starts 6.95)")
                continue
            if sh.shape_type == 1:  # autoshape
                try: fc = "#" + str(sh.fill.fore_color.rgb)
                except Exception: fc = None
                try: lc = "#" + str(sh.line.color.rgb) if sh.line.fill.type == 1 else None
                except Exception: lc = None
                if sh.auto_shape_type == 9: d.ellipse([x, y, x + w, y + h], fill=fc, outline=lc, width=2)
                else: d.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=fc, outline=lc, width=2)
                continue
            if sh.has_text_frame and sh.text_frame.text.strip():
                if sh.name == "Speaker tag" or True:
                    p0 = sh.text_frame.paragraphs[0]
                    if p0.alignment is not None and int(p0.alignment) == 2:
                        # centered: draw per paragraph centered
                        cy = y + 3
                        for p in sh.text_frame.paragraphs:
                            r = p.runs[0]; f = font(r.font.size.pt, bool(r.font.bold)); ls = wrap(d, "".join(q.text for q in p.runs), f, w - 10)
                            if sh.text_frame.vertical_anchor is not None and int(sh.text_frame.vertical_anchor) == 3: cy = y + (h - len(ls) * r.font.size.pt * PX / 72 * 1.2) / 2
                            for ln in ls: d.text((x + (w - d.textlength(ln, font=f)) / 2, cy), ln, font=f, fill="#" + str(r.font.color.rgb)); cy += r.font.size.pt * PX / 72 * 1.2
                        continue
                    if p0.alignment is not None and int(p0.alignment) == 3:  # right
                        r = p0.runs[0]; f = font(r.font.size.pt, bool(r.font.bold)); d.text((x + w - 5 - d.textlength(r.text, font=f), y + (h - r.font.size.pt * PX / 72) / 2), r.text, font=f, fill="#" + str(r.font.color.rgb)); continue
                    draw_text(d, sh.text_frame, x, y, w, h, tag)
        im.save(f"{outdir}/slide{n:02d}.png")
render(sys.argv[1], sys.argv[2]); print("\n".join(issues) or "no overflow issues detected")

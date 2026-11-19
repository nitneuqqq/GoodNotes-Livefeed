from PIL import Image, ImageDraw

from tutor import changed, thumb

page = Image.new("RGB", (1000, 1000), "white")
assert not changed(thumb(page), thumb(page.copy()))

written = page.copy()
ImageDraw.Draw(written).line((100, 100, 300, 120), fill="black", width=8)  # a pen stroke
assert changed(thumb(page), thumb(written))

noisy = page.copy()
noisy.putpixel((500, 500), (230, 230, 230))  # faint compression speck
assert not changed(thumb(page), thumb(noisy))

print("ok")

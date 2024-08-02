from PIL import Image, ImageDraw
import os

# Vytvoříme základní ikonu
def create_icon(size, filename):
    image = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    # Nakreslíme jednoduchý červený kruh
    radius = size // 4
    center = size // 2
    draw.ellipse(
        (center - radius, center - radius, center + radius, center + radius),
        fill=(255, 0, 0, 255))

    # Uložíme obrázek
    image.save(filename, "PNG")


# Seznam velikostí ikon pro .iconset
sizes = [16, 32, 64, 128, 256, 512, 1024]


iconset_folder = "MyApp.iconset"
os.makedirs(iconset_folder, exist_ok=True)

# Vygenerujeme obrázky v různých velikostech
for size in sizes:
    filename = f"{iconset_folder}/icon_{size}x{size}.png"
    create_icon(size, filename)
    print(f"Created {filename}")

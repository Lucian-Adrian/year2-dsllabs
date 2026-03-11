from PIL import Image, ImageDraw, ImageFont
import os

repodir = os.path.dirname(__file__)
if not os.path.isdir(repodir):
    os.makedirs(repodir)

width, height = 800, 400
img = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(img)

# Try to get a default font
try:
    font = ImageFont.truetype('arial.ttf', size=14)
except Exception:
    font = ImageFont.load_default()

# positions
positions = {
    'TensorScript Source': (50, 50),
    'src/lexer.py': (200, 50),
    'src/tokens.py': (350, 50),
    'LexicalError': (500, 50),
    'CLI Output': (200, 200),
    'Streamlit Observatory': (350, 200),
    'src/highlighter.py': (500, 200),
}

# draw boxes and text
for label, (x, y) in positions.items():
    # compute text size using textbbox (compatible across PIL versions)
    try:
        bbox = draw.textbbox((0, 0), label, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
    except Exception:
        # fallback for very old versions
        w, h = font.getsize(label)
    padding = 10
    draw.rectangle([x, y, x + w + padding, y + h + padding], outline='black')
    draw.text((x + 5, y + 5), label, fill='black', font=font)

# draw one arrow
# simple directional line

draw.line([100, 60, 200, 60], fill='black', width=2)

img_path = os.path.join(repodir, 'architecture_diagram.png')
img.save(img_path)
print('Generated', img_path)

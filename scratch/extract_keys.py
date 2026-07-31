import re
import json

svg_path = "d:/0_projektek/billentyuzet_dev/zmk_2025/docs/images/layout.svg"

with open(svg_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all circles
circles = re.findall(r'<circle\s+cx="([\d\.]+)"\s+cy="([\d\.]+)"\s+r="([\d\.]+)"', content)

parsed_circles = []
for cx, cy, r in circles:
    parsed_circles.append({
        "cx": float(cx),
        "cy": float(cy),
        "r": float(r)
    })

# filter radius 2.88mm (which is 60 circles)
target_circles = [c for c in parsed_circles if round(c['r'], 2) == 2.88]

left_half = []
right_half = []

for c in target_circles:
    if c['cx'] < 210: # Assuming 210 is center (SVG width is 420)
        left_half.append(c)
    else:
        right_half.append(c)

print(f"Left half: {len(left_half)} switches")
print(f"Right half: {len(right_half)} switches")

# Let's sort left_half by Y then X
left_half.sort(key=lambda c: (round(c['cy']/10)*10, c['cx']))

for i, c in enumerate(left_half):
    print(f"SW{i+1}: ({c['cx']:.2f}, {c['cy']:.2f})")

# Dump to json
with open("d:/0_projektek/billentyuzet_dev/zmk_2025/scratch/keys_left.json", "w") as f:
    json.dump([{'x': c['cx'], 'y': c['cy']} for c in left_half], f, indent=2)


import re
import json

svg_path = "d:/0_projektek/billentyuzet_dev/zmk_2025/docs/images/layout.svg"
with open(svg_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all circles
circles = re.findall(r'<circle\s+cx="([\d\.]+)"\s+cy="([\d\.]+)"\s+r="([\d\.]+)"', content)
target_circles = []
for cx, cy, r in circles:
    if round(float(r), 2) == 2.88:
        target_circles.append({
            "cx": float(cx),
            "cy": float(cy)
        })

left_half = [c for c in target_circles if c['cx'] < 210]
right_half = [c for c in target_circles if c['cx'] > 210]

# Generate SVG
min_x = min(k['cx'] for k in left_half + right_half) - 10
min_y = min(k['cy'] for k in left_half + right_half) - 10
max_x = max(k['cx'] for k in left_half + right_half) + 10
max_y = max(k['cy'] for k in left_half + right_half) + 10

v_width = max_x - min_x
v_height = max_y - min_y

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{v_width}mm" height="{v_height}mm" viewBox="{min_x} {min_y} {v_width} {v_height}">
  <defs>
    <style>
      .key {{ fill: #161b22; stroke: #58a6ff; stroke-width: 0.5px; rx: 2.61px; ry: 2.61px; }}
      .key-inner {{ fill: none; stroke: #58a6ff; stroke-width: 0.28px; rx: 0.95px; ry: 0.95px; }}
    </style>
  </defs>
  <g id="Shape">
  <!-- You could place the PCB outline here if available -->
  </g>
  <g id="Keycaps">
'''

key_w = 17.5
key_h = 17.5
inner_w = 12
inner_h = 12

for k in left_half + right_half:
    cx = k['cx']
    cy = k['cy']
    
    # Calculate rotation if any
    r = 0
    if cx > 100 and cx < 110 and cy > 155 and cy < 165: r = -15
    elif cx > 120 and cx < 130 and cy > 160 and cy < 170: r = -30
    elif cx > 135 and cx < 145 and cy > 170 and cy < 180: r = -60
    elif cx > 310 and cx < 320 and cy > 155 and cy < 165: r = 15
    elif cx > 290 and cx < 300 and cy > 160 and cy < 170: r = 30
    elif cx > 270 and cx < 280 and cy > 170 and cy < 180: r = 60
    
    transform = f'transform="rotate({r}, {cx}, {cy})"' if r != 0 else ''
    
    x = cx - key_w/2
    y = cy - key_h/2
    ix = cx - inner_w/2
    iy = cy - inner_h/2
    
    svg += f'    <rect class="key" x="{x}" y="{y}" width="{key_w}" height="{key_h}" {transform} />\n'
    svg += f'    <rect class="key-inner" x="{ix}" y="{iy}" width="{inner_w}" height="{inner_h}" {transform} />\n'

svg += '''  </g>
</svg>
'''

with open("d:/0_projektek/billentyuzet_dev/zmk_2025/docs/images/v4_2_layout.svg", "w") as f:
    f.write(svg)
print("SVG Generated.")

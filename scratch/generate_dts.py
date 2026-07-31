import json

# Physical coordinates for Left Half
coords = {
    (0,3): (82.50, 73.00),
    (0,0): (25.50, 82.00),
    (0,1): (44.50, 80.50),
    (0,2): (63.50, 76.50),
    (0,4): (101.50, 79.50),
    (0,5): (120.50, 83.00),
    
    (1,3): (82.50, 92.01),
    (1,0): (25.50, 101.00),
    (1,1): (44.50, 99.50),
    (1,2): (63.50, 95.50),
    (1,4): (101.50, 98.50),
    (1,5): (120.50, 102.00),
    
    (2,2): (63.50, 114.50),
    (2,3): (82.50, 111.00),
    (2,0): (25.50, 120.00),
    (2,1): (44.50, 118.50),
    (2,4): (101.50, 117.50),
    (2,5): (120.50, 121.00),
    
    (3,2): (63.50, 133.50),
    (3,3): (82.50, 130.00),
    (3,0): (25.50, 139.00),
    (3,1): (44.50, 137.50),
    (3,4): (101.50, 136.79),
    (3,5): (120.50, 140.29),
    
    (4,1): (31.00, 158.00),  # Ctrl
    (4,2): (50.00, 158.00),  # Alt
    (4,3): (77.00, 159.00),  # Encoder / Win
    (4,4): (104.84, 160.81), # Thumb L
    (4,5): (123.26, 166.00), # Thumb _
    (5,5): (139.95, 175.35)  # Thumb R
}

nav_x, nav_y = 141.00, 149.00
coords[(0,6)] = (nav_x, nav_y - 7) # Up
coords[(1,6)] = (nav_x, nav_y + 7) # Down
coords[(2,6)] = (nav_x + 7, nav_y) # Right
coords[(3,6)] = (nav_x - 7, nav_y) # Left
coords[(4,6)] = (nav_x, nav_y)     # Center (M)

rots = {
    (4,4): -15,
    (4,5): -30,
    (5,5): -60
}

min_x = 25.50 - 9.525
min_y = 73.00 - 9.525

phys_keys = []

# Map has 6 rows, 14 columns
for r in range(6):
    # Left half (c = 0..6)
    for c in range(7):
        if (r,c) in coords:
            cx, cy = coords[(r,c)]
            rot = rots.get((r,c), 0)
            w = 18 if (r,c) not in [(0,6),(1,6),(2,6),(3,6)] else 8
            h = 18 if (r,c) not in [(0,6),(1,6),(2,6),(3,6)] else 8
            
            tl_x = cx - w/2
            tl_y = cy - h/2
            zx = round((tl_x - min_x) * 100 / 19.05)
            zy = round((tl_y - min_y) * 100 / 19.05)
            zw = round(w * 100 / 19.05)
            zh = round(h * 100 / 19.05)
            phys_keys.append(f"<&key_physical_attrs {zw} {zh} {zx} {zy} {rot} 0 0>")
        else:
            # Dummy key
            phys_keys.append(f"<&key_physical_attrs 0 0 0 0 0 0 0>")
            
    # Right half (c = 7..13)
    for c in range(7):
        # The right half is mirrored from the left half
        if (r,c) in coords:
            cx, cy = coords[(r,c)]
            rot = -rots.get((r,c), 0)
            w = 18 if (r,c) not in [(0,6),(1,6),(2,6),(3,6)] else 8
            h = 18 if (r,c) not in [(0,6),(1,6),(2,6),(3,6)] else 8
            
            cx = 420 - cx
            
            if c == 6:
                if r == 2: cx -= 14
                if r == 3: cx += 14
                
            tl_x = cx - w/2
            tl_y = cy - h/2
            zx = round((tl_x - min_x) * 100 / 19.05)
            zy = round((tl_y - min_y) * 100 / 19.05)
            zw = round(w * 100 / 19.05)
            zh = round(h * 100 / 19.05)
            phys_keys.append(f"<&key_physical_attrs {zw} {zh} {zx} {zy} {rot} 0 0>")
        else:
            phys_keys.append(f"<&key_physical_attrs 0 0 0 0 0 0 0>")

print("\\n=== PHYSICAL LAYOUT ===")
print("    physical_layout0: physical_layout_0 {")
print("        compatible = \"zmk,physical-layout\";")
print("        display-name = \"Default Layout\";")
print("        keys")
print("            = " + "\\n              , ".join(phys_keys))
print("            ;")
print("    };")

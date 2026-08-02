import re
import sys
import shutil

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add #define BLUE 4
    if '#define BLUE' not in content:
        content = content.replace('#define ADJ  3', '#define ADJ  3\n#define BLUE 4')

    # 2. Extract space combos
    combo_pattern = re.compile(r'(combo_([a-z0-9_]+)_space\s*\{\s*timeout-ms = <\d+>;\s*key-positions = <(\d+) (61)>;\s*bindings = <([^>]+)>;\s*\};)')
    combos = combo_pattern.findall(content)
    
    if not combos:
        print(f"No space combos found in {filepath}!")
        return

    macros_text = ""
    for full_match, name, pos1, pos2, binding in combos:
        macro_name = f"macro_{name}_space"
        macros_text += f"""
        {macro_name}: {macro_name} {{
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            wait-ms = <0>;
            tap-ms = <0>;
            bindings = <&macro_press &mo BLUE>, <&macro_tap {binding}>, <&macro_pause_for_release>, <&macro_release &mo BLUE>;
        }};"""
        
        # Replace the combo's binding with the macro and add slow-release
        new_combo = f"combo_{name}_space {{ timeout-ms = <60>; key-positions = <{pos1} {pos2}>; bindings = <&{macro_name}>; slow-release; }};"
        content = content.replace(full_match, new_combo)

    # 3. Add macros to the macros block
    if 'macros {' in content:
        content = content.replace('macros {', 'macros {' + macros_text)

    # 4. Generate BLUE layer matrix
    # Based on the mappings, create a dictionary of pos -> binding
    pos_map = {int(p): b for _, _, p, _, b in combos}
    
    blue_layer_rows = []
    blue_layer_rows.append("                blue_layer {")
    blue_layer_rows.append("                        bindings = <")
    for r in range(6):
        start_idx = r * 14
        row_str = "    "
        for c in range(14):
            idx = start_idx + c
            if idx in pos_map:
                val = pos_map[idx]
            else:
                val = "&trans"
            row_str += f"{val:<11}"
        blue_layer_rows.append(row_str)
    blue_layer_rows.append(">;")
    blue_layer_rows.append("                };")
    
    blue_layer_text = "\n".join(blue_layer_rows)
    
    # 5. Add blue_layer before the closing brace of keymap
    content = content.replace("                };", "                };\n\n" + blue_layer_text, 1)

    # 6. Change base layer space to &lt BLUE SPACE
    # Search for &kp SPACE at position 61
    # 4,0(56) 4,1(57) 4,2(58) 4,3(59) 4,4(60) 4,5(61)
    # Actually just replace `&kp SPACE` with `&lt BLUE SPACE`
    # But wait! &kp SPACE is only used once in the base layer in that row?
    # Let's do a precise string replacement on row 4
    row4_pattern = re.compile(r'(&kp N1\s+&kp LCTRL\s+&kp LALT\s+&kp LGUI\s+&kp ENTER\s+)&kp SPACE(\s+&kp M\s+&kp M\s+&kp N9\s+&kp N8\s+&kp RGUI\s+&kp BSPC\s+&lt NAV SPACE\s+&kp N0)')
    content = row4_pattern.sub(r'\1&lt BLUE SPACE\2', content)

    # Backup and save
    shutil.copy2(filepath, filepath + '.bak')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Successfully processed {filepath}")

if __name__ == "__main__":
    process_file("config/boards/shields/v4_2/v4_2.keymap")
    process_file("config/boards/shields/v4_2_da/v4_2_da.keymap")

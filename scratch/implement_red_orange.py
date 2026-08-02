import re
import sys
import shutil

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update #defines
    # Replace the whole block of defines to ensure correct indices
    define_pattern = re.compile(r'#define BASE 0\n#define NAV  2\n#define SYM  3\n#define ADJ  4\n#define BLUE 1')
    if define_pattern.search(content):
        new_defines = """#define BASE 0\n#define BLUE 1\n#define RED 2\n#define ORANGE 3\n#define NAV  4\n#define SYM  5\n#define ADJ  6"""
        content = define_pattern.sub(new_defines, content)
    else:
        # Fallback if it was different
        if '#define RED 2' not in content:
            content = content.replace('#define BLUE 1', '#define BLUE 1\n#define RED 2\n#define ORANGE 3')

    # Helper function to process combos for a layer
    def process_combos(color_name, key_pos, layer_name):
        nonlocal content
        # color_name: 'red' or 'orange'
        # key_pos: '60' or '75'
        # layer_name: 'RED' or 'ORANGE'
        combo_pattern = re.compile(rf'(combo_([a-z0-9_]+)_{color_name}\s*\{{\s*timeout-ms = <\d+>;\s*key-positions = <(\d+) ({key_pos})>;\s*bindings = <([^>]+)>;\s*\}};\s*)')
        combos = combo_pattern.findall(content)
        
        if not combos:
            print(f"No {color_name} combos found in {filepath}!")
            return "", []

        macros_text = ""
        pos_map = {}
        for full_match, name, pos1, pos2, binding in combos:
            macro_name = f"macro_{name}_{color_name}"
            macros_text += f"""
        {macro_name}: {macro_name} {{
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            wait-ms = <0>;
            tap-ms = <0>;
            bindings = <&macro_press &mo {layer_name}>, <&macro_tap {binding}>, <&macro_pause_for_release>, <&macro_release &mo {layer_name}>;
        }};"""
            
            # Replace the combo's binding with the macro and add slow-release
            # We preserve exactly the formatting up to bindings
            new_combo = f"combo_{name}_{color_name} {{ timeout-ms = <60>; key-positions = <{pos1} {pos2}>; bindings = <&{macro_name}>; slow-release; }};\n    "
            content = content.replace(full_match, new_combo)
            
            pos_map[int(pos1)] = binding
            
        # Build layer matrix
        layer_rows = []
        layer_rows.append(f"                {color_name}_layer {{")
        layer_rows.append("                        bindings = <")
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
            layer_rows.append(row_str)
        layer_rows.append(">;")
        layer_rows.append("                };")
        
        return "\n".join(layer_rows), macros_text

    red_layer_text, red_macros = process_combos('red', '60', 'RED')
    orange_layer_text, orange_macros = process_combos('orange', '75', 'ORANGE')

    # 3. Add macros to the macros block
    all_macros = red_macros + orange_macros
    if all_macros and 'macros {' in content:
        content = content.replace('macros {', 'macros {' + all_macros)

    # 4. Insert layers at the end of keymap
    # Find the end of the keymap block
    # It usually ends with `        };\n};`
    layers_text = ""
    if red_layer_text:
        layers_text += "\n\n" + red_layer_text
    if orange_layer_text:
        layers_text += "\n\n" + orange_layer_text
        
    content = content.replace("        };\n};", layers_text + "\n        };\n};")

    # 5. Change base layer keys
    # Replace &kp ENTER with &lt RED ENTER on row 4
    # Note: \s+ matches any whitespace, \b ensures word boundary
    content = re.sub(r'(\b)kp ENTER(\b)', r'\1lt RED ENTER\2', content)
    # Replace &kp DEL with &lt ORANGE DEL on row 5
    content = re.sub(r'(\b)kp DEL(\b)', r'\1lt ORANGE DEL\2', content)

    # Backup and save
    shutil.copy2(filepath, filepath + '.bak2')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Successfully processed {filepath}")

if __name__ == "__main__":
    process_file("config/boards/shields/v4_2/v4_2.keymap")
    process_file("config/boards/shields/v4_2_da/v4_2_da.keymap")

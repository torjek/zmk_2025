import re
import sys
import shutil

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add Pointing Include
    if '<dt-bindings/zmk/pointing.h>' not in content:
        content = content.replace('#include <dt-bindings/zmk/keys.h>', '#include <dt-bindings/zmk/keys.h>\n#include <dt-bindings/zmk/pointing.h>')

    # 2. Add custom behaviors
    if 'td_shift: tap_dance_shift {' not in content:
        behaviors_inject = """
    behaviors {
        td_shift: tap_dance_shift {
            compatible = "zmk,behavior-tap-dance";
            #binding-cells = <0>;
            tapping-term-ms = <200>;
            bindings = <&sk LSHFT>, <&kp CAPSLOCK>;
        };

        inc_dec_msc: behavior_sensor_rotate_msc {
            compatible = "zmk,behavior-sensor-rotate-var";
            #sensor-binding-cells = <2>;
            bindings = <&msc>, <&msc>;
        };
    };
"""
        # Inject into behaviors block if it exists, otherwise create it before macros
        if 'behaviors {' in content:
            content = content.replace('behaviors {', 'behaviors {' + behaviors_inject.replace('    behaviors {', '').replace('    };\n', ''))
        else:
            content = content.replace('    macros {', behaviors_inject + '\n    macros {')

    # 3. Modify base layer
    # Replace &sk LSHFT with &td_shift in the first column of row 3
    content = content.replace('    &sk LSHFT  &kp Z', '    &td_shift  &kp Z')

    # 4. Modify sensor bindings
    content = content.replace('&inc_dec_kp C_VOL_UP C_VOL_DN', '&inc_dec_msc SCRL_DOWN SCRL_UP')

    # 5. Disable other capslock triggers
    # Comment out the combos if not already commented
    content = re.sub(r'^[ \t]*(combo_shift_red[ \t]*\{)', r'    // \1', content, flags=re.MULTILINE)
    content = re.sub(r'^[ \t]*(combo_shift_orange[ \t]*\{)', r'    // \1', content, flags=re.MULTILINE)

    # Replace &kp CAPSLOCK in the matrix
    content = re.sub(r'^[ \t]*&kp CAPSLOCK', r'    &trans      ', content, flags=re.MULTILINE)

    # Backup and save
    shutil.copy2(filepath, filepath + '.encoder.bak')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Successfully processed {filepath}")

if __name__ == "__main__":
    process_file("config/boards/shields/v4_2/v4_2.keymap")
    process_file("config/boards/shields/v4_2_da/v4_2_da.keymap")

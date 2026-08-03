import re
import os
import shutil

def update_keymap(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add #ifndef SIMPLE_MODE block at the top, right after includes
    if '#ifndef SIMPLE_MODE' not in content:
        # Find the last include line
        last_include_idx = content.rfind('#include')
        end_of_line = content.find('\n', last_include_idx) + 1
        
        simple_mode_def = """
#ifndef SIMPLE_MODE
#define SIMPLE_MODE 0
#endif
"""
        content = content[:end_of_line] + simple_mode_def + content[end_of_line:]

    # 2. Add mac_git macro
    mac_git_def = """
        mac_git: mac_git {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            wait-ms = <30>;
            tap-ms = <30>;
            bindings = <&macro_tap &kp G &kp I &kp T &kp SPACE &kp S &kp T &kp A &kp T &kp U &kp S &kp ENTER>;
        };
"""
    if 'mac_git {' not in content:
        content = content.replace('    macros {', '    macros {' + mac_git_def)

    # 3. Add the #if SIMPLE_MODE block in the base layer
    # The line is: &kp ESC    &kp N1     &kp N2     &kp N3     &kp N4     &kp N5
    # Be careful to preserve the right side of the split if it's on the same line.
    
    # Look for the start of the row
    target_row = r'(^[ \t]*&kp ESC[ \t]+&kp N1[ \t]+&kp N2[ \t]+&kp N3[ \t]+&kp N4[ \t]+&kp N5)(.*)'
    replacement = r'''#if SIMPLE_MODE == 1
\1\2
#else
    &kp ESC    &kp C_AL_CALC &kp LG(DOT) &kp LS(LG(S)) &mac_git   &kp LG(V)\2
#endif'''
    
    content = re.sub(target_row, replacement, content, flags=re.MULTILINE)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {filepath}")


update_keymap('config/boards/shields/v4_2/v4_2.keymap')
update_keymap('config/boards/shields/v4_2_da/v4_2_da.keymap')

# 4. Clean up the macro folders
shutil.rmtree('config/boards/shields/v4_2_da_macro', ignore_errors=True)
shutil.rmtree('config/boards/shields/v4_2_macro', ignore_errors=True)

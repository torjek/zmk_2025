import re

filepath = 'config/boards/shields/v4_2_macro/v4_2_macro.keymap'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add mac_git macro
mac_git_def = """
        mac_git: mac_git {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            wait-ms = <30>;
            tap-ms = <30>;
            bindings = <&macro_tap &kp G &kp I &kp T &kp SPACE &kp S &kp T &kp A &kp T &kp U &kp S &kp ENTER>;
        };
"""
# Insert it into the macros block
if 'mac_git {' not in content:
    content = content.replace('    macros {', '    macros {' + mac_git_def)

# 2. Replace N1..N5 on the base layer left half top row
# Look for: &kp ESC    &kp N1     &kp N2     &kp N3     &kp N4     &kp N5
# Replace with: &kp ESC    &kp C_AL_CALC &kp LG(DOT) &kp LS(LG(S)) &mac_git   &kp LG(V)
content = content.replace(
    '&kp ESC    &kp N1     &kp N2     &kp N3     &kp N4     &kp N5',
    '&kp ESC    &kp C_AL_CALC &kp LG(DOT) &kp LS(LG(S)) &mac_git   &kp LG(V)'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated v4_2_da_macro.keymap")

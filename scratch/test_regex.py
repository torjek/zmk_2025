import re

text = """
    //combo_n1_red { timeout-ms = <60>; key-positions = <1 60>; bindings = <&kp N6>; }; 
    combo_q_red  { timeout-ms = <60>; key-positions = <15 60>; bindings = <&kp LS(NUHS)>; }; 
    combo_w_red  { timeout-ms = <60>; key-positions = <16 60>; bindings = <&kp KP_N7>; };    
    combo_f_red  { timeout-ms = <60>; key-positions = <17 60>; bindings = <&kp KP_N8>; };    
    combo_p_red  { timeout-ms = <60>; key-positions = <18 60>; bindings = <&kp KP_N9>; };    
    combo_g_red  { timeout-ms = <60>; key-positions = <19 60>; bindings = <&kp LS(NUBS)>; };    
"""

color_name = 'red'
key_pos = '60'
combo_pattern = re.compile(rf'^[ \t]*(combo_([a-z0-9_]+)_{color_name}\s*\{{\s*timeout-ms = <\d+>;\s*key-positions = <(\d+) ({key_pos})>;\s*bindings = <([^>]+)>;\s*\}};[ \t]*)', re.MULTILINE)

matches = combo_pattern.findall(text)
for m in matches:
    print(f"Matched: {m[1]}")

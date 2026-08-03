import os
import shutil

src_dir = 'config/boards/shields/v4_2_da'
dst_dir = 'config/boards/shields/v4_2_da_macro'

os.makedirs(dst_dir, exist_ok=True)

# 1. Kconfig.shield
kconfig_content = """config SHIELD_V4_2_DA_MACRO_LEFT
    def_bool $(shields_list_contains,v4_2_da_macro_left)

config SHIELD_V4_2_DA_MACRO_RIGHT
    def_bool $(shields_list_contains,v4_2_da_macro_right)
"""
with open(os.path.join(dst_dir, 'Kconfig.shield'), 'w') as f:
    f.write(kconfig_content)

# 2. Overlays
with open(os.path.join(dst_dir, 'v4_2_da_macro_left.overlay'), 'w') as f:
    f.write('#include "../v4_2/v4_2_left.overlay"\n')

with open(os.path.join(dst_dir, 'v4_2_da_macro_right.overlay'), 'w') as f:
    f.write('#include "../v4_2/v4_2_right.overlay"\n')

# 3. Confs
shutil.copy2(os.path.join(src_dir, 'v4_2_da_left.conf'), os.path.join(dst_dir, 'v4_2_da_macro_left.conf'))
shutil.copy2(os.path.join(src_dir, 'v4_2_da_right.conf'), os.path.join(dst_dir, 'v4_2_da_macro_right.conf'))

# 4. Keymap
shutil.copy2(os.path.join(src_dir, 'v4_2_da.keymap'), os.path.join(dst_dir, 'v4_2_da_macro.keymap'))

import os
import shutil

src_dir = 'd:/0_projektek/billentyuzet_dev/zmk_torjek/zmk/app/boards/arm/bluemicro840'
dst_dir = 'd:/0_projektek/billentyuzet_dev/zmk_2025/config/boards/torjek/monogreen'

os.makedirs(dst_dir, exist_ok=True)

def copy_and_replace(filename_src, filename_dst=None):
    if filename_dst is None:
        filename_dst = filename_src
    
    with open(os.path.join(src_dir, filename_src), 'r') as f:
        content = f.read()
    
    # Replace identifiers
    content = content.replace('bluemicro840', 'monogreen')
    content = content.replace('BLUEMICRO840', 'MONOGREEN')
    content = content.replace('BlueMicro840', 'MonoGreen')
    content = content.replace('BlueMicro', 'MonoGreen')
    
    with open(os.path.join(dst_dir, filename_dst), 'w') as f:
        f.write(content)

# 1. Kconfig files
copy_and_replace('Kconfig')
copy_and_replace('Kconfig.board', 'Kconfig.monogreen')
copy_and_replace('Kconfig.defconfig')

# 2. DTS and Defconfig
copy_and_replace('bluemicro840_v1.dts', 'monogreen.dts')
copy_and_replace('bluemicro840_v1-pinctrl.dtsi', 'monogreen-pinctrl.dtsi')
copy_and_replace('bluemicro840_v1_defconfig', 'monogreen_defconfig')

# 3. CMake files
copy_and_replace('board.cmake')
copy_and_replace('pre_dt_board.cmake')

# 4. Pro micro pins (Copy verbatim)
shutil.copy2(os.path.join(src_dir, 'arduino_pro_micro_pins.dtsi'), os.path.join(dst_dir, 'arduino_pro_micro_pins.dtsi'))

# 5. Create board.yml (HWMv2 required)
board_yml = """board:
  name: monogreen
  vendor: torjek
  socs:
    - name: nrf52840
"""
with open(os.path.join(dst_dir, 'board.yml'), 'w') as f:
    f.write(board_yml)

# 6. Create monogreen.yaml (HWMv2 metadata)
monogreen_yaml = """identifier: monogreen
name: MonoGreen
type: mcu
arch: arm
toolchain:
  - zephyr
  - gnuarmemb
  - xtools
supported:
  - adc
  - usb_device
  - ble
  - ieee802154
  - pwm
  - watchdog
"""
with open(os.path.join(dst_dir, 'monogreen.yaml'), 'w') as f:
    f.write(monogreen_yaml)

print("Created monogreen board successfully.")

# Copyright (c) 2026 MonoTypist
# SPDX-License-Identifier: MIT
#
# Code that this repository adds to ZMK. Read by the build because zephyr/module.yml points here.

if ((NOT CONFIG_ZMK_SPLIT) OR CONFIG_ZMK_SPLIT_ROLE_CENTRAL)
  target_sources_ifdef(CONFIG_ZMK_BEHAVIOR_LPOS app PRIVATE src/behaviors/behavior_lpos.c)
endif()

if(CONFIG_SHIELD_V4_2_LEFT OR CONFIG_SHIELD_V4_2_RIGHT)
  zephyr_library()
  zephyr_library_sources_ifdef(CONFIG_IS31FL3733 is31fl3733_init.c)
endif()

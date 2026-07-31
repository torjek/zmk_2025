#include <zephyr/device.h>
#include <zephyr/drivers/led.h>
#include <zephyr/init.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(is31fl3733_init, LOG_LEVEL_DBG);

static int is31fl3733_turn_on(void) {
#if DT_HAS_COMPAT_STATUS_OKAY(issi_is31fl3733)
    const struct device *led_dev = DEVICE_DT_GET_ANY(issi_is31fl3733);
    
    if (!led_dev) {
        LOG_ERR("Could not find IS31FL3733 device");
        return -ENODEV;
    }

    if (!device_is_ready(led_dev)) {
        LOG_ERR("IS31FL3733 device is not ready");
        return -ENODEV;
    }

    LOG_INF("Found IS31FL3733 device, turning on all LEDs");

    // The IS31FL3733 has up to 192 LEDs (12x16 matrix)
    for (int i = 0; i < 192; i++) {
        // Set brightness to 100 (range is 0-100 in Zephyr LED API)
        int err = led_set_brightness(led_dev, i, 100);
        if (err && err != -ENOTSUP) {
            LOG_WRN("Failed to set brightness for LED %d (err %d)", i, err);
        }
        led_on(led_dev, i);
    }
#else
    LOG_INF("No IS31FL3733 device found in device tree for this board half.");
#endif
    return 0;
}

// Run this during application initialization
SYS_INIT(is31fl3733_turn_on, APPLICATION, CONFIG_APPLICATION_INIT_PRIORITY);

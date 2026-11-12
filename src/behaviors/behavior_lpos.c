/*
 * Copyright (c) 2026 MonoTypist
 *
 * SPDX-License-Identifier: MIT
 */

/*
 * "&lpos LAYER POSITION": layer position lookup.
 *
 * A MonoTypist combo is "letter key + thumb key". It must send the key that the thumb's layer holds
 * at the letter's position, and keep that layer on while the keys stay down. Until now each combo
 * had its own macro with the key written into it, so the macros repeated the layer tables:
 *
 *     <&macro_press &mo BLUE>, <&macro_tap &kp SEMI>, <&macro_pause_for_release>, <&macro_release &mo BLUE>
 *
 * This behaviour does the same steps, but reads the key from the layer when the combo fires. A key
 * changed with ZMK Studio is then sent by the combo too, with no new firmware.
 *
 * The key is tapped (pressed and let go at once), as in the macros. A held key would repeat for as
 * long as the thumb stays down, because the combos use "slow-release".
 */

#define DT_DRV_COMPAT zmk_behavior_lpos

#include <string.h>

#include <zephyr/device.h>
#include <drivers/behavior.h>
#include <zephyr/logging/log.h>

#include <zmk/behavior.h>
#include <zmk/behavior_queue.h>
#include <zmk/keymap.h>
#include <zmk/matrix.h>

LOG_MODULE_DECLARE(zmk, CONFIG_ZMK_LOG_LEVEL);

#if DT_HAS_COMPAT_STATUS_OKAY(DT_DRV_COMPAT)

#if IS_ENABLED(CONFIG_ZMK_BEHAVIOR_METADATA)

/* What ZMK Studio shows for the two parameters. */
static const struct behavior_parameter_value_metadata param1_values[] = {
    {
        .display_name = "Layer",
        .type = BEHAVIOR_PARAMETER_VALUE_TYPE_LAYER_ID,
    },
};

static const struct behavior_parameter_value_metadata param2_values[] = {
    {
        .display_name = "Key position",
        .type = BEHAVIOR_PARAMETER_VALUE_TYPE_RANGE,
        .range = {.min = 0, .max = (int32_t)ZMK_KEYMAP_LEN - 1},
    },
};

static const struct behavior_parameter_metadata_set param_metadata_set[] = {{
    .param1_values = param1_values,
    .param1_values_len = ARRAY_SIZE(param1_values),
    .param2_values = param2_values,
    .param2_values_len = ARRAY_SIZE(param2_values),
}};

static const struct behavior_parameter_metadata metadata = {
    .sets_len = ARRAY_SIZE(param_metadata_set),
    .sets = param_metadata_set,
};

#endif /* IS_ENABLED(CONFIG_ZMK_BEHAVIOR_METADATA) */

static int lpos_keymap_binding_pressed(struct zmk_behavior_binding *binding,
                                       struct zmk_behavior_binding_event event) {
    const zmk_keymap_layer_id_t layer = binding->param1;
    const uint16_t position = binding->param2;

    /* Layer on first, as the macros did: the keys typed while the thumb stays down use it. */
    int err = zmk_keymap_layer_activate(layer, false);
    if (err < 0) {
        LOG_ERR("lpos: cannot turn on layer %d (err %d)", layer, err);
        return err;
    }

    const struct zmk_behavior_binding *found = zmk_keymap_get_layer_binding_at_idx(layer, position);
    if (found == NULL || found->behavior_dev == NULL) {
        LOG_WRN("lpos: no key at position %d on layer %d", position, layer);
        return ZMK_BEHAVIOR_OPAQUE;
    }

    /* A layer key that is itself "&lpos" would call this function without end. */
    if (strcmp(found->behavior_dev, binding->behavior_dev) == 0) {
        LOG_WRN("lpos: position %d on layer %d is an lpos key, skipped", position, layer);
        return ZMK_BEHAVIOR_OPAQUE;
    }

    LOG_DBG("lpos: layer %d position %d sends %s 0x%02x 0x%02x", layer, position,
            found->behavior_dev, found->param1, found->param2);

    /* Tap it through the same queue the macros use, so it keeps its place among their keys. */
    const struct zmk_behavior_binding key = *found;
    err = zmk_behavior_queue_add(&event, key, true, 0);
    if (err < 0) {
        LOG_ERR("lpos: behaviour queue is full (err %d)", err);
        return ZMK_BEHAVIOR_OPAQUE;
    }
    err = zmk_behavior_queue_add(&event, key, false, 0);
    if (err < 0) {
        /* The press is already queued: let the key go directly, so it cannot stay down. */
        zmk_behavior_invoke_binding(&key, event, false);
    }

    return ZMK_BEHAVIOR_OPAQUE;
}

static int lpos_keymap_binding_released(struct zmk_behavior_binding *binding,
                                        struct zmk_behavior_binding_event event) {
    return zmk_keymap_layer_deactivate(binding->param1, false);
}

static const struct behavior_driver_api behavior_lpos_driver_api = {
    .binding_pressed = lpos_keymap_binding_pressed,
    .binding_released = lpos_keymap_binding_released,
#if IS_ENABLED(CONFIG_ZMK_BEHAVIOR_METADATA)
    .parameter_metadata = &metadata,
#endif /* IS_ENABLED(CONFIG_ZMK_BEHAVIOR_METADATA) */
};

#define LPOS_INST(n)                                                                               \
    BEHAVIOR_DT_INST_DEFINE(n, NULL, NULL, NULL, NULL, POST_KERNEL,                                \
                            CONFIG_KERNEL_INIT_PRIORITY_DEFAULT, &behavior_lpos_driver_api);

DT_INST_FOREACH_STATUS_OKAY(LPOS_INST)

#endif /* DT_HAS_COMPAT_STATUS_OKAY(DT_DRV_COMPAT) */

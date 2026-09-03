"""WCAG contrast utilities shared by Kaizen diagnostics and presets."""

WCAG_AA_NORMAL_TEXT_RATIO = 4.5


def relative_luminance(color):
    """Return WCAG relative luminance for a ``#RRGGBB`` color."""
    if not isinstance(color, str):
        raise ValueError("color must be a #RRGGBB string")
    value = color.strip()
    if value.startswith("#"):
        value = value[1:]
    if len(value) != 6:
        raise ValueError(f"expected #RRGGBB, got {color!r}")
    try:
        channels = tuple(int(value[index:index + 2], 16) / 255 for index in (0, 2, 4))
    except ValueError as exc:
        raise ValueError(f"expected #RRGGBB, got {color!r}") from exc

    linear = tuple(
        channel / 12.92 if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    )
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(foreground, background):
    """Return the WCAG contrast ratio between two ``#RRGGBB`` colors."""
    foreground_luminance = relative_luminance(foreground)
    background_luminance = relative_luminance(background)
    return (max(foreground_luminance, background_luminance) + 0.05) / (
        min(foreground_luminance, background_luminance) + 0.05
    )


def find_low_contrast_pairs(colors):
    """Return WCAG-AA warnings for text/background pairs in a theme palette.

    Kaizen's GTK templates define normal text as ``fg`` over ``bg`` and selected
    text as ``bg`` over ``accent``.  The latter directly maps to
    ``theme_selected_fg_color`` and ``theme_selected_bg_color``.
    """
    pairs = (
        ("theme_fg_color", colors.get("fg"), "theme_bg_color", colors.get("bg")),
        (
            "theme_selected_fg_color",
            colors.get("bg"),
            "theme_selected_bg_color",
            colors.get("accent"),
        ),
    )
    warnings = []
    for foreground_name, foreground, background_name, background in pairs:
        if foreground is None or background is None:
            continue
        ratio = contrast_ratio(foreground, background)
        if ratio < WCAG_AA_NORMAL_TEXT_RATIO:
            warnings.append(
                f"{foreground_name} ({foreground}) vs {background_name} ({background}): "
                f"{ratio:.2f}:1; minimum required {WCAG_AA_NORMAL_TEXT_RATIO:.1f}:1"
            )
    return warnings

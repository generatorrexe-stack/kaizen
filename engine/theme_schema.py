"""Versioning and in-memory migration for Kaizen theme TOML documents."""

CURRENT_THEME_SCHEMA_VERSION = 2

DEFAULT_SECTIONS = {
    "icons": {"icon_theme": "Adwaita"},
    "cursor": {"cursor_theme": "Adwaita", "cursor_size": 24},
    "font": {"font_name": "Cantarell 11"},
    "gtk": {"prefer_dark_theme": "1"},
}


def migrate_theme_data(data, source="theme"):
    """Return ``(theme, notices)`` after migrating known older schemas.

    Migration is deliberately in memory: opening or listing a legacy community
    theme never rewrites its source file. Applying it is therefore safe even on
    read-only theme collections.
    """
    if not isinstance(data, dict):
        raise ValueError(f"{source}: theme document must be a TOML table")

    migrated = dict(data)
    try:
        version = int(migrated.get("schema_version", 0))
    except (TypeError, ValueError):
        raise ValueError(f"{source}: schema_version must be an integer")

    notices = []
    if version > CURRENT_THEME_SCHEMA_VERSION:
        notices.append(
            f"{source}: schema_version {version} is newer than supported "
            f"{CURRENT_THEME_SCHEMA_VERSION}; continuing without downgrade"
        )
        return migrated, notices

    if version < CURRENT_THEME_SCHEMA_VERSION:
        for section, defaults in DEFAULT_SECTIONS.items():
            value = migrated.get(section)
            if not isinstance(value, dict):
                value = {}
            migrated[section] = {**defaults, **value}
        migrated["schema_version"] = CURRENT_THEME_SCHEMA_VERSION
        notices.append(
            f"{source}: migrated schema_version {version} → "
            f"{CURRENT_THEME_SCHEMA_VERSION} in memory"
        )
    return migrated, notices

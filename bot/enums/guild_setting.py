from enum import Enum


class GuildSetting(Enum):
    DEBUG = "debug"
    PREFIX = "prefix"

    RULES_CHANNEL = "rules"
    MODERATION_CHANNEL = "moderation"

    MIN_MOD_ROLE = "minmod"
    MUTED_ROLE = "muted"
    WARNING_ROLE = "warning"

from enum import Enum


class ModerationType(Enum):
    BAN = "baneado"
    WARN = "advertido"
    KICK = "expulsado"
    MUTE = "silenciado"
    UNBAN = "desbaneado"
    UNMUTE = "des-silenciado"

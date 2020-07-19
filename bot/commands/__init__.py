from .bot_config import BotConfigCmds
from .moderation import ModerationCmds
from .server_config import ServerConfigCmds
from .unmoderation import UnModerationCmds
from .user import UserCmds


def setup(bot):
    bot.add_cog(UserCmds(bot))
    bot.add_cog(ModerationCmds(bot))
    bot.add_cog(UnModerationCmds(bot))
    bot.add_cog(ServerConfigCmds(bot))
    bot.add_cog(BotConfigCmds(bot))

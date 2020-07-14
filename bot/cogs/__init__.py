from .listeners import Listeners


def setup(bot):
    bot.add_cog(Listeners(bot))

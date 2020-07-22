"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

from .listeners import Listeners


def setup(bot):
    bot.add_cog(Listeners(bot))

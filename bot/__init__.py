"""
Copyright 2020 Fazt Community ~ All rights reserved. MIT license.
"""

import logging

logging.basicConfig(
    filename="latest.log",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d:%(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)

# Copyright (C) 2021 Ahmed Alkadhim
#
# This file is part of Random Sakuga.
#
# Random Sakuga is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Random Sakuga is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Random Sakuga.  If not, see <http://www.gnu.org/licenses/>.

import logging


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler_format = logging.Formatter(
    "%(levelname)s<%(asctime)s>%(module)s - %(funcName)s - %(lineno)d - %(message)s",
    "%Y-%m-%d %H:%M:%S",
)
strream_handler_format = logging.Formatter("%(levelname)s - %(module)s - %(message)s")

file_handler = logging.FileHandler("RandomSakuga.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(file_handler_format)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
stream_handler.setFormatter(strream_handler_format)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

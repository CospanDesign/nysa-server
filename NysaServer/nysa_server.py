# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

# This file is part of Nysa (wiki.cospandesign.com/index.php?title=Nysa).
#
# Nysa is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Nysa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nysa; If not, see <http://www.gnu.org/licenses/>.


# -*- coding: utf-8 -*-

"""
nysa-video-server

Application to be run as a daemon

The application listens on a socket at 12591

The first socket opened is the control socket where
user then sends commands down to open addional domain
specific sockets, for example to open up a socket to
receive video images the JSON string

"
{
    "video":{
        "port":"12599",
        "width":480,
        "height":272,
        "fourcc":"RGBA"
    }
}

The server will then open up a port where it will expect to receive images at the above frame

Users sends and received data to/from a nysa device

Format of a data frame
"""

import sys
import os

from server import tcp_server
from nysa.common import status
from nysa.host import platform_scanner



from server import control_server

def main(port, debug = False):
    print "Start a server on port: %d" % port
    print "Debug :%s" % str(debug)
    s = status.Status()
    if debug:
        s.set_level("verbose")

    s.Info("Find Nysa Device")

    nysa = platform_scanner.get_platforms(s)[0]
    control_server.start_control_server_sync(host = "localhost", port = port, nysa = nysa)


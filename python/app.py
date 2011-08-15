# -*- coding: utf-8 -*-
#
# Copyright (C) 2011  Tiger Soldier
#
# This file is part of OSD Lyrics.
# 
# OSD Lyrics is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OSD Lyrics is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OSD Lyrics.  If not, see <http://www.gnu.org/licenses/>. 
#/

from optparse import OptionParser
import glib
import dbus
import dbus.service
import consts
from dbus.mainloop.glib import DBusGMainLoop

__all__ = (
    'App',
    )

class App(object):
    """ Basic class to create a component application for OSD Lyrics.

    The application creates a mainloop, owns a DBus name, and exits when the bus
    name of OSD Lyrics disappears.

    Once the app is created, it will parse `sys.argv`. The accepted arguments are:

     - `-w`, `--watch-daemon`: If not empty, watch the daemon with given bus name.
       The default value is the bus name of OSD Lyrics
    
    To create an component application owning the bus name ``org.osdlyrics.MyApp``,
    just simply follow the code below:

      app = osdlyrics.App('MyApp')
      app.run()
    """
    
    def __init__(self, name, watch_daemon=True):
        """
        
        Arguments:
        - `name`: The suffix of the bus name. The full bus name is
          `org.osdlyrics.` + name
        - `watch_daemon`: Whether to watch daemon bus
        """
        self._name = name
        self._namewatch = None
        self._watch_daemon = watch_daemon
        self._loop = glib.MainLoop()
        self._conn = dbus.SessionBus(mainloop=DBusGMainLoop())
        self._bus_name = dbus.service.BusName(consts.APP_BUS_PREFIX + name,
                                              self._conn)
        self._parse_options()
        
    def _parse_options(self):
        parser = OptionParser()
        parser.add_option('-w', '--watch-daemon',
                          dest='watch_daemon',
                          action='store',
                          default=consts.BUS_NAME,
                          metavar='BUS_NAME',
                          help='A well-known bus name on DBus. Exit when the ' \
                          'name disappears. If set to empty string, this player ' \
                          'proxy will not exit.')
        (options, args) = parser.parse_args()
        if self._watch_daemon:
            self._watch_daemon_bus(options.watch_daemon)
        
    def _watch_daemon_bus(self, name):
        if len(name) > 0:
            self._namewatch = self._conn.watch_name_owner(name,
                                                          self._daemon_name_changed)

    def _daemon_name_changed(self, name):
        if len(name) == 0:
            self._loop.quit()
            if (self._namewatch is not None):
                self._namewatch.cancel()
                self._namewatch = None

    @property
    def connection(self):
        """The DBus connection of the app"""
        return self._conn

    def run(self):
        """Runs the main loop"""
        self._loop.run()

    def quit(self):
        """Quits the main loop"""
        self._loop.quit()

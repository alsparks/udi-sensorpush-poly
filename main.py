#!/usr/bin/env python3
"""
Polyglot v3 SensorPush node server
Copyright (C) 2022 Alan Sparks

MIT License
"""

import udi_interface
import sys
from nodes import ctl

LOGGER = udi_interface.LOGGER

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

        # Create the controller node
        ctl.ControllerNode(polyglot, 'controller', 'controller', 'SensorPushNodeServer')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)


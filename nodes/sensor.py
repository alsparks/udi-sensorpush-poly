#!/usr/bin/env python3
"""
Polyglot v3 SensorPush node server
Copyright (C) 2022 Alan Sparks

MIT License
"""
import udi_interface
import sys

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

'''
This is our device node.
'''
class SensorNode(udi_interface.Node):
    id='sensor'
    drivers = [{'driver': 'ST', 'value': 1, 'uom': 56}, #Polyglot connection status
                {'driver': 'GV1', 'value': 0, 'uom': 565}, #Blue Iris Server Status (0=red, 1=green, 2=yellow, 3=disconnected)
                {'driver': 'GV2', 'value':0, 'uom': 72} #Blue Iris Profile
                {'driver': 'GV3', 'value':0, 'uom': 131} #Blue Iris Profile
                ]


    def __init__(self, polyglot, parent, address, name):
        super(SensorNode, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot

        self.Parameters = Custom(polyglot, 'customparams')

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)

    '''
    Read the user entered custom parameters
    '''
    def parameterHandler(self, params):
        self.Parameters.load(params)


#!/usr/bin/env python3
"""
Polyglot v3 SensorPush node server
Copyright (C) 2022 Alan Sparks

MIT License
"""

import udi_interface
import sys
import time
from pysensorpush import PySensorPush
from nodes import sensor


LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

'''
Controller is interfacing with both Polyglot and the device.
'''
class Controller(udi_interface.Node):
    id = 'ctl'
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            ]

    def __init__(self, polyglot, parent, address, name):
        super(Controller, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.n_queue = []

        self.Parameters = Custom(polyglot, 'customparams')

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.STOP, self.stop)
        polyglot.subscribe(polyglot.START, self.start, address)
        polyglot.subscribe(polyglot.ADDNODEDONE, self.node_queue)
        polyglot.subscribe(polyglot.POLL, self.poll)

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)

    '''
    node_queue() and wait_for_node_event() create a simple way to wait
    for a node to be created.  The nodeAdd() API call is asynchronous and
    will return before the node is fully created. Using this, we can wait
    until it is fully created before we try to use it.
    '''
    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    '''
    Read the user entered custom parameters.  Here is where the user will
    configure the number of child nodes that they want created.
    '''
    def parameterHandler(self, params):
        self.Parameters.load(params)
        self.poly.Notices.clear()
        try:
            if 'user' in params:
                self.user = params['user']
            else:
                self.user = ""

            if 'password' in params:
                self.password = params['password']
            else:
                self.password = ""

            if self.user == "" or self.password == "":
                LOGGER.error('SensorPush requires \'user\' and \'password\' parameters to be specified in custom configuration.')
                self.poly.Notices['cfg'] = 'Please enter user and password.'
                return False
            else:
                if self.connect():
                    self.discover()
        except Exception as ex:
            LOGGER.error('Error starting Blue Iris NodeServer: %s', str(ex))

        self.createChildren()


    '''
    This is called when the node is added to the interface module. It is
    run in a separate thread.  This is only run once so you should do any
    setup that needs to be run initially.  For example, if you need to
    start a thread to monitor device status, do it here.

    Here we load the custom parameter configuration document and push
    the profiles to the ISY.
    '''
    def start(self):
        self.poly.setCustomParamsDoc()
        # Not necessary to call this since profile_version is used from server.json
        self.poly.updateProfile()
        LOGGER.info('Started SensorPush NodeServer for v3 NodeServer')


    '''
    Create the children nodes.  Since this will be called anytime the
    user changes the number of nodes and the new number may be less
    than the previous number, we need to make sure we create the right
    number of nodes.  Because this is just a simple example, we'll first
    delete any existing nodes then create the number requested.
    '''
    def createChildren(self):
        LOGGER.info('Login to Sensorpush')
        self.spapi = PySensorPush(self.user, self.password)
        sensors = self.spapi.sensors

        self.nodes = {}
        for sensorid, values in sensors.items():
            address = values['deviceId']
            title = values['name']
            try:
                node = sensor.SensorNode(self.poly, self.address, address, title)
                self.poly.addNode(node)
                self.wait_for_node_done()
                self.nodes[address] = node
            except Exception as e:
                LOGGER.error('Failed to create {}: {}'.format(title, e))



    def poll(self, polltype):
        if 'shortPoll' in polltype:
            LOGGER.info('SensorPush starting poll')
            samples = sp.samples()
            sensors = sp.sensors
            for sensorid, values in samples['sensors'].items():
                LOGGER.info('SensorPush sensorid {}'.format(sensorid))
                deviceid = sensorid.split('.')[0]
                battery = sensors[sensorid]['battery_voltage']
                name = sensors[sensorid]['name']
                rssi = sensors[sensorid]['rssi']
                type = sensors[sensorid]['type']
                temperature = values[0]['temperature']
                humidity = values[0]['humidity']

                node = self.nodes[deviceid]
                node.setDriver('ST', temperature, False, False)
                node.setDriver('GV1', humidity, False, False)
                node.setDriver('GV2', battery, False, False)
                node.setDriver('GV3', rssi, False, False)


    '''
    Change all the child node active status drivers to false
    '''
    def stop(self):

        nodes = self.poly.getNodes()
        for node in nodes:
            if node != 'controller':   # but not the controller node
                nodes[node].setDriver('ST', 0, True, True)

        self.poly.stop()


    '''
    Just to show how commands are implemented. The commands here need to
    match what is in the nodedef profile file. 
    '''
    def noop(self):
        LOGGER.info('Discover not implemented')

    commands = {'DISCOVER': noop}

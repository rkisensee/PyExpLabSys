# pylint: disable=R0913, C0103

import threading
import time
import PyExpLabSys.drivers.bronkhorst as bronkhorst
from PyExpLabSys.common.loggers import ContinuousLogger
from PyExpLabSys.common.value_logger import ValueLogger
from PyExpLabSys.common.sockets import DateDataPullSocket
from PyExpLabSys.common.sockets import DataPushSocket
from PyExpLabSys.common.sockets import LiveSocket
import credentials

class FlowControl(threading.Thread):
    """ Keep updated values of the current flow """
    def __init__(self, mfcs, pullsocket, pushsocket, livesocket):
        threading.Thread.__init__(self)
        self.mfcs = mfcs
        print mfcs
        self.pullsocket = pullsocket
        self.pushsocket = pushsocket
        self.livesocket = livesocket
        self.running = True
        self.reactor_pressure = float('NaN')

    def value(self):
        """ Helper function for the reactor logger functionality """
        return self.reactor_pressure

    def run(self):
        while self.running:
            time.sleep(0.1)
            qsize = self.pushsocket.queue.qsize()
            print "Qsize: " + str(qsize)
            while qsize > 0:
                element = self.pushsocket.queue.get()
                mfc = element.keys()[0]
                self.mfcs[mfc].set_flow(element[mfc])
                qsize = self.pushsocket.queue.qsize()

            for mfc in self.mfcs:
                flow =  self.mfcs[mfc].read_flow()
                #print(mfc + ': ' + str(flow))
                self.pullsocket.set_point_now(mfc, flow)
                self.livesocket.set_point_now(mfc, flow)
                if mfc == 'M13201551A':
                    print "Pressure: " + str(flow)
                    self.reactor_pressure = flow

port = '/dev/serial/by-id/usb-FTDI_USB-RS485_Cable_FTWGRR44-if00-port0'
devices = ['M13201551A', 'M8203814C', 'M11200362F',
           'M8203814A', 'M8203814B', 'M11200362B', 'M11200362H']
ranges = {}
ranges['M13201551A'] = 5 # Microreactor, pressure controller
ranges['M8203814C'] = 2.5 #Conrad
ranges['M11200362F'] = 1 # Microreactor, flow 2
ranges['M8203814A'] = 10 # flow 5 (argon calibrated)
ranges['M8203814B'] = 3 # Microreactor, flow 1 (argon calibrated)
ranges['M11200362B'] = 10 # Palle Flow
ranges['M11200362H'] = 2.5 # Palle pressure
name = {}

MFCs = {}
print '!'
for i in range(0, 8):
    error = 0
    name[i] = ''
    while (error < 3) and (name[i]==''):
        # Pro forma-range will be update in a few lines
        bronk = bronkhorst.Bronkhorst('/dev/ttyUSB' + str(i), 1) 
        name[i] = bronk.read_serial()
        name[i] = name[i].strip()
        error = error + 1
        print error
        print name[i]
    if name[i] in devices:
        MFCs[name[i]] = bronkhorst.Bronkhorst('/dev/ttyUSB' + str(i),
                                              ranges[name[i]])
        MFCs[name[i]].set_control_mode() #Accept setpoint from rs232
        print name[i]

Datasocket = DateDataPullSocket('microreactor_mfc_control',
                                devices,
                                timeouts=[3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0],
                                port=9000)
Datasocket.start()

Pushsocket = DataPushSocket('microreactor_mfc_control', action='enqueue')
Pushsocket.start()
Livesocket = LiveSocket('microreactor_mfc_control', devices, 1)
Livesocket.start()

fc = FlowControl(MFCs, Datasocket, Pushsocket, Livesocket)
fc.start()

Logger = ValueLogger(fc, comp_val=1, comp_type='log', low_comp=0.0001)
Logger.start()

db_logger = ContinuousLogger(table='dateplots_microreactor',
                             username=credentials.user,
                             password=credentials.passwd,
                             measurement_codenames=['mr_reactor_pressure'])
db_logger.start()

while True:
    time.sleep(0.25)
    v = Logger.read_value()
    if Logger.read_trigged():
        print v
        db_logger.enqueue_point_now('mr_reactor_pressure', v)
        Logger.clear_trigged()


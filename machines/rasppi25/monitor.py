"""Continuous logger for the Pfeiffer gauges on the theta probe"""

import time
from PyExpLabSys.drivers.pfeiffer import TPG262
from PyExpLabSys.common.loggers import ContinuousLogger
from PyExpLabSys.common.utilities import get_logger
from PyExpLabSys.common.sockets import LiveSocket
import credentials


LOGGER = get_logger('thetaprobe_pressure_logger', file_log=True)


def main():
    """The main method for the pressure logger"""

    # Open communication to the pressure measurement unit
    tpg = TPG262(port='/dev/ttyUSB0', baudrate=9600)
    LOGGER.info('Initiated driver to TPG 262')

    # Get a continuous logger
    codenames = ['thetaprobe_pressure_loadlock', 'thetaprobe_pressure_uvgun']
    db_logger = ContinuousLogger(table='dateplots_thetaprobe',
                                 username=credentials.USERNAME,
                                 password=credentials.PASSWORD,
                                 measurement_codenames=codenames)
    db_logger.start()
    LOGGER.info('Initiated and started database logger')

    name = 'Thetaprobe pressure load lock and UV gun'
    livesocket = LiveSocket(name, codenames, 0.2)
    livesocket.start()

    loadlock_last = {'value': 1E20, 'time': 0}
    uvgun_last = {'value': 1E20, 'time': 0}

    try:
        while True:
            # get the values: returns:
            # (value1, (status_code1, status_message1),
            # value2, (status_code2, status_message2))
            try:
                value_ll, code_ll, value_uv, code_uv = tpg.pressure_gauges()
            except IOError:
                LOGGER.info(
                    'Serial communication failed. Sleep 10 and try again.')
                time.sleep(10)
                continue
            livesocket.set_point_now('thetaprobe_pressure_loadlock', value_ll)
            livesocket.set_point_now('thetaprobe_pressure_uvgun', value_uv)

            ### Load lock
            if code_ll[0] in [0, 1]:  # If measurement is OK or underranged
                if logging_criteria(value_ll, loadlock_last):
                    LOGGER.info('Add value {} for load lock'.format(value_ll))
                    now_ll = db_logger.enqueue_point_now(
                        'thetaprobe_pressure_loadlock',
                        value_ll)
                    loadlock_last['value'] = value_ll
                    loadlock_last['time'] = now_ll

            ### UV gun
            if code_uv[0] in [0, 1]:  # If measurement is OK or underranged
                if logging_criteria(value_uv, uvgun_last):
                    LOGGER.info('Add value {} for UV gun'.format(value_uv))
                    now_uv = db_logger.enqueue_point_now(
                        'thetaprobe_pressure_uvgun',
                        value_uv)
                    uvgun_last['value'] = value_uv
                    uvgun_last['time'] = now_uv
    except KeyboardInterrupt:
        LOGGER.info('Keyboard interrupt. Shutting down')
        db_logger.stop()
        livesocket.stop()
        LOGGER.info('Database logger stoppped. Exiting!')


def logging_criteria(value, last):
    """Evaluate if the point should be logged. The criteria is if the value has
    changed more than 10% from the last logged value or if it has been more
    than 10 min since last logged point
    """
    change = abs(value - last['value']) / last['value'] > 0.1
    timeout = time.time() - last['time'] > 600
    return change or timeout


if __name__ == '__main__':
    try:
        main()
    except:
        LOGGER.exception("Program stopped due to the following exception")
        raise

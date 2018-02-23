import logging
import time
import requests
import settings
from conapi import ConApi
from scan import ScanDevice

logging.basicConfig(
    format="[agent %(asctime)s] %(levelname)s %(message)s",
    level=logging.WARN)

INTERVAL_AGENT_RESTART = 5
INTERVAL_AGENT_WAIT = 5


class Agent(object):
    def __init__(self):
        self._devices = {}
        self.api = ConApi(settings.DMC_API_URI)
        self.is_connected = False

    def run(self):
        logging.info('agent starting')
        while True:
            if self.is_connected:
                latest = ScanDevice.scan()
                # latest = self.random_dervice()
                rsp = self.api.update_list(latest)  # could be None if request failed
                if not rsp or rsp.status_code is not requests.codes.ok:
                    logging.warn('failed to update device list on server')
                    self.is_connected = False
                    time.sleep(INTERVAL_AGENT_RESTART)
                else:
                    logging.info('successfully updated list, sleep for %s s', INTERVAL_AGENT_WAIT)
                    time.sleep(INTERVAL_AGENT_WAIT)

            else:
                rsp = self.api.clear_list()
                if not rsp or rsp.status_code is not requests.codes.ok:
                    logging.warn('retry in %s s', INTERVAL_AGENT_RESTART)
                    time.sleep(INTERVAL_AGENT_RESTART)
                else:
                    logging.info('connected to server, clearing device list')
                    self.is_connected = True
                    self._devices.clear()


if __name__ == '__main__':
    agent = Agent()
    agent.run()

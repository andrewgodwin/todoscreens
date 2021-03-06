from micropython import const
import logging
import uasyncio as asyncio
from core.constants import *

#  buttonMask:
#
#  -------------------------
#  |                       |
#  |                       |
#  |       SyncSign        |
#  |                       |
#  |                       |
#  -------------------------
#  |  1  |  2  |  4  |  8  |
#  -------------------------

BUTTON_MASK_1 = const(1)
BUTTON_MASK_2 = const(2)
BUTTON_MASK_3 = const(4)
BUTTON_MASK_4 = const(8)
BUTTON_STATUS_PRESSED = const(0)

UPDATE_TOKEN = "???"
REFRESH_URL = "https://todoscreens.aeracode.org/update/%s" % UPDATE_TOKEN
ONE_DONE_URL = "https://todoscreens.aeracode.org/update/%s/done/1" % UPDATE_TOKEN
TWO_DONE_URL = "https://todoscreens.aeracode.org/update/%s/done/2" % UPDATE_TOKEN
THREE_DONE_URL = "https://todoscreens.aeracode.org/update/%s/done/3" % UPDATE_TOKEN

log = logging.getLogger("APP")
log.setLevel(logging.DEBUG)


class App:
    # User App of Hub SDK, trigger an http request to IFTTT when a button event occurs

    def __init__(self, mgr, loop, pan):
        self.pan = pan
        self.loop = loop
        mgr.setPanCallback(self.onPanEvent)
        log.info("App Starting")

    def onPanEvent(self, event, data):
        if event == EVT_NODE_BUTTONS:
            self.onNodeButtonEvent(data["nodeId"], data["buttonMask"], data["status"])

    def onNodeButtonEvent(self, nodeId, buttonMask, status):
        """Event of button pressed
        When the button is pressed, this method will be called by system
        Args:
            nodeId: (int) indicates which node is changing its status
            buttonMask: (int) =1, first button; =2, second button; =4, third button; =8, fourth button;
            status: (int) =0, button pressed
        """
        log.info("Got button event %s" % buttonMask)
        if buttonMask == BUTTON_MASK_1 and status == BUTTON_STATUS_PRESSED:
            self.loop.create_task(self.postRequest(ONE_DONE_URL))
        elif buttonMask == BUTTON_MASK_2 and status == BUTTON_STATUS_PRESSED:
            self.loop.create_task(self.postRequest(TWO_DONE_URL))
        elif buttonMask == BUTTON_MASK_3 and status == BUTTON_STATUS_PRESSED:
            self.loop.create_task(self.postRequest(THREE_DONE_URL))
        elif buttonMask == BUTTON_MASK_4 and status == BUTTON_STATUS_PRESSED:
            self.loop.create_task(self.postRequest(REFRESH_URL))

    async def postRequest(self, url):
        log.info("Requesting %s" % url)
        import arequests as requests

        response = None
        resultStr = None
        try:
            response = await requests.post(
                url, headers={"Content-Length": "0"}, data=None, verify=False
            )
            resultStr = await response.text
        except Exception as e:
            log.exception(e, "request fail: %r" % e)
        if response:
            log.info("status code: %d", response.status_code)
            await response.close()
            log.info("POST result: %s", resultStr)

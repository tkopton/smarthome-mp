import constants
from constants import ADAPTER_KIND
from constants import ADAPTER_NAME
from constants import HOST_IDENTIFIER
from constants import PORT_IDENTIFIER
from constants import USER_CREDENTIAL
from constants import PASSWORD_CREDENTIAL

from restcall import RestClient


class DeviceCollector:
    def __init__(self, adapter_instance, token, fqdn, result, logger):
        self.fqdn = fqdn
        self.token = token
        self.result = result
        self.logger = logger
        self.adapter_instance = adapter_instance

    def collect(self):
        host = self.adapter_instance.get_identifier_value(constants.HOST_IDENTIFIER)
        port = self.adapter_instance.get_identifier_value(constants.PORT_IDENTIFIER)
        base_url = "http://" + str(host) + ":" + str(port)
        headers = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate'
        }
        client = RestClient(base_url)
        # Make a GET request to the /users endpoint
        status_code, response_data = client.get("device", headers)
        if status_code == 200:
            self.logger.info("POST request successful!")
            self.logger.info("Status code: " + str(status_code))
            # logger.info("Response data: " + str(response_data))
            for obj in response_data:
                self.logger.info("Device ID:" + obj["id"])
                self.logger.info("Serial Number:" + obj["serialNumber"])
                self.logger.info("Serial Number:" + obj["config"]["name"])
                # creating object and adding it to the result set
                device_obj = self.result.object(ADAPTER_KIND, "device", obj["config"]["name"])
                device_obj.with_property(
                    "id", obj["id"]
                )
                device_obj.with_property(
                    "serialnumber", obj["serialNumber"]
                )
                device_obj.with_metric(
                    "version", obj["version"]
                )
        else:
            self.logger.error("Error:", status_code)

        return self.result

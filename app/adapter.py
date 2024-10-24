#  Copyright 2022 VMware, Inc.
#  SPDX-License-Identifier: Apache-2.0
import json
import sys
from typing import List

import aria.ops.adapter_logging as logging
from aria.ops.adapter_instance import AdapterInstance
from aria.ops.definition.adapter_definition import AdapterDefinition
from aria.ops.result import CollectResult
from aria.ops.result import EndpointResult
from aria.ops.result import TestResult
from aria.ops.timer import Timer

import constants
from constants import ADAPTER_KIND
from constants import ADAPTER_NAME
from constants import HOST_IDENTIFIER
from constants import PORT_IDENTIFIER
from constants import USER_CREDENTIAL
from constants import PASSWORD_CREDENTIAL
from restcall import RestClient
from collectDevices import DeviceCollector

logger = logging.getLogger(__name__)

def get_adapter_definition() -> AdapterDefinition:
    """
    The adapter definition defines the object types and attribute types (metric/property) that are present
    in a collection. Setting these object types and attribute types helps VMware Aria Operations to
    validate, process, and display the data correctly.
    :return: AdapterDefinition
    """
    with Timer(logger, "Get Adapter Definition"):
        definition = AdapterDefinition(ADAPTER_KIND, ADAPTER_NAME)

        definition.define_string_parameter(
            "ID",
            label="ID",
            description="Example identifier. Using a value of 'bad' will cause "
                        "test connection to fail; any other value will pass.",
            required=True,
        )
        # The key 'container_memory_limit' is a special key that is read by the VMware Aria Operations collector to
        # determine how much memory to allocate to the docker container running this adapter. It does not
        # need to be read inside the adapter code.
        definition.define_int_parameter(
            "container_memory_limit",
            label="Adapter Memory Limit (MB)",
            description="Sets the maximum amount of memory VMware Aria Operations can "
                        "allocate to the container running this adapter instance.",
            required=True,
            advanced=True,
            default=1024,
        )

        definition.define_string_parameter(
            constants.HOST_IDENTIFIER,
            label="Host",
            description="FQDN or IP of the SmartHome Central Unit.",
            required=True,
            default="192.168.0.116",
        )

        definition.define_int_parameter(
            constants.PORT_IDENTIFIER,
            label="TCP Port",
            description="TCP Port SmartHome is listening on.",
            required=True,
            advanced=True,
            default=8080,
        )

        credential = definition.define_credential_type("smarthome_user", "Credential")
        credential.define_string_parameter(constants.USER_CREDENTIAL, "User Name")
        credential.define_password_parameter(constants.PASSWORD_CREDENTIAL, "Password")

        # Object types definition section

        system = definition.define_object_type("system", "System")
        system.define_string_property("systemid", "SystemID")
        device = definition.define_object_type("device", "Device")
        device.define_string_property("id", "ID")
        device.define_string_property("serialnumber", "Serial Number")
        device.define_string_property("name", "Name")
        device.define_metric("version", "Version")

        logger.debug(f"Returning adapter definition: {definition.to_json()}")
        return definition


def test(adapter_instance: AdapterInstance) -> TestResult:
    with Timer(logger, "Test"):
        result = TestResult()
        try:
            # Sample test connection code follows. Replace with your own test connection
            # code. A typical test connection will generally consist of:
            # 1. Read identifier values from adapter_instance that are required to
            #    connect to the target(s)
            # 2. Connect to the target(s), and retrieve some sample data
            # 3. Disconnect cleanly from the target (ensure this happens even if an
            #    error occurs)
            # 4. If any of the above failed, return an error, otherwise pass.

            # Read the 'ID' identifier in the adapter instance and use it for a
            # connection test.

            # my code START
            host = adapter_instance.get_identifier_value(constants.HOST_IDENTIFIER)
            port = adapter_instance.get_identifier_value(constants.PORT_IDENTIFIER)
            base_url = "http://" + str(host) + ":" + str(port)
            logger.info(base_url)
            # base_url = "http://192.168.0.116:8080"
            # Define the JSON payload
            user = adapter_instance.get_credential_value(constants.USER_CREDENTIAL)
            password = adapter_instance.get_credential_value(constants.PASSWORD_CREDENTIAL)
            payload = {
                "username": user,
                "password": password,
                "grant_type": "password"
            }

            # Define the headers with Authorization
            headers = {
                'Authorization': 'Basic Y2xpZW50SWQ6Y2xpZW50UGFzcw==',  # Replace YOUR_ACCESS_TOKEN with your actual access token
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate'
            }

            # Convert payload to JSON string
            json_payload = json.dumps(payload)

            client = RestClient(base_url)
            # Make a GET request to the /users endpoint
            status_code, response_data = client.post("auth/token", headers, json_payload)
            if status_code == 200:
                logger.info("POST request successful!")
                logger.info("Status code: " + str(status_code))
                logger.info("Response data: " + str(response_data))
                sh_token = response_data.get("access_token")
                logger.info("B-Token: " + sh_token)
            else:
                logger.error("Error:", status_code)

            client = None
            headers = None
            headers = {
                'Authorization': 'Bearer ' + sh_token,
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate'
            }
            client = RestClient(base_url)
            # Make a GET request to the /users endpoint
            status_code, response_data = client.get("status", headers)
            if status_code == 200:
                logger.info("POST request successful!")
                logger.info("Status code: " + str(status_code))
                # logger.info("Response data: " + str(response_data))
            else:
                logger.error("Error:", status_code)
            # my code END

            id = adapter_instance.get_identifier_value("ID")

            # In this case the adapter does not need to connect
            # to anything, as it reads directly from the host it is running on.
            if id is None:
                result.with_error("No ID Found")
            elif id.lower() == "bad":
                # As there is not an actual failure condition to test for, this
                # example only shows the mechanics of reading identifiers and
                # constructing test results. Here we add an error to the result
                # that is returned.
                result.with_error("The ID is bad")
            # otherwise, the test has passed
        except Exception as e:
            logger.error("Unexpected connection test error")
            logger.exception(e)
            result.with_error("Unexpected connection test error: " + repr(e))
        finally:
            # TODO: If any connections are still open, make sure they are closed before returning
            # logger.debug(f"Returning test result: {result.get_json()}")
            return result


def collect(adapter_instance: AdapterInstance) -> CollectResult:
    with Timer(logger, "Collection"):
        result = CollectResult()
        try:
            # Sample collection code follows. Replace this with your own collection
            # code. A typical collection will generally consist of:
            # 1. Read identifier values from adapter_instance that are required to
            #    connect to the target(s)
            # 2. Connect to the target(s), and retrieve data
            # 3. Add the data into a CollectResult's objects, properties, metrics, etc
            # 4. Disconnect cleanly from the target (ensure this happens even if an
            #    error occurs)
            # 5. Return the CollectResult.

            # my code START
            host = adapter_instance.get_identifier_value(constants.HOST_IDENTIFIER)
            port = adapter_instance.get_identifier_value(constants.PORT_IDENTIFIER)
            base_url = "http://" + str(host) + ":" + str(port)
            logger.info(base_url)
            # base_url = "http://192.168.0.116:8080"
            # Define the JSON payload
            user = adapter_instance.get_credential_value(constants.USER_CREDENTIAL)
            password = adapter_instance.get_credential_value(constants.PASSWORD_CREDENTIAL)
            payload = {
                "username": user,
                "password": password,
                "grant_type": "password"
            }

            # Define the headers with Authorization
            headers = {
                'Authorization': 'Basic Y2xpZW50SWQ6Y2xpZW50UGFzcw==',
                # Replace YOUR_ACCESS_TOKEN with your actual access token
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate'
            }

            # Convert payload to JSON string
            json_payload = json.dumps(payload)

            client = RestClient(base_url)
            # Make a GET request to the /users endpoint
            status_code, response_data = client.post("auth/token", headers, json_payload)
            if status_code == 200:
                sh_token = response_data.get("access_token")
            else:
                logger.error("Error:", status_code)

            devicecollector = DeviceCollector(adapter_instance, sh_token, host, result, logger)
            result = devicecollector.collect()

            # my code END

        except Exception as e:
            logger.error("Unexpected collection error")
            logger.exception(e)
            result.with_error("Unexpected collection error: " + repr(e))
        finally:
            # TODO: If any connections are still open, make sure they are closed before returning
            logger.debug(f"Returning collection result {result.get_json()}")
            return result


def get_endpoints(adapter_instance: AdapterInstance) -> EndpointResult:
    with Timer(logger, "Get Endpoints"):
        result = EndpointResult()
        # In the case that an SSL Certificate is needed to communicate to the target,
        # add each URL that the adapter uses here. Often this will be derived from a
        # 'host' parameter in the adapter instance. In this Adapter we don't use any
        # HTTPS connections, so we won't add any. If we did, we might do something like
        # this:
        # result.with_endpoint(adapter_instance.get_identifier_value("host"))
        #
        # Multiple endpoints can be returned, like this:
        # result.with_endpoint(adapter_instance.get_identifier_value("primary_host"))
        # result.with_endpoint(adapter_instance.get_identifier_value("secondary_host"))
        #
        # This 'get_endpoints' method will be run before the 'test' method,
        # and VMware Aria Operations will use the results to extract a certificate from
        # each URL. If the certificate is not trusted by the VMware Aria Operations
        # Trust Store, the user will be prompted to either accept or reject the
        # certificate. If it is accepted, the certificate will be added to the
        # AdapterInstance object that is passed to the 'test' and 'collect' methods.
        # Any certificate that is encountered in those methods should then be validated
        # against the certificate(s) in the AdapterInstance.
        logger.debug(f"Returning endpoints: {result.get_json()}")
        return result


# Main entry point of the adapter. You should not need to modify anything below this line.
def main(argv: List[str]) -> None:
    logging.setup_logging("adapter.log")
    # Start a new log file by calling 'rotate'. By default, the last five calls will be
    # retained. If the logs are not manually rotated, the 'setup_logging' call should be
    # invoked with the 'max_size' parameter set to a reasonable value, e.g.,
    # 10_489_760 (10MB).
    logging.rotate()
    logger.info(f"Running adapter code with arguments: {argv}")
    if len(argv) != 3:
        # `inputfile` and `outputfile` are always automatically appended to the
        # argument list by the server
        logger.error("Arguments must be <method> <inputfile> <ouputfile>")
        exit(1)

    method = argv[0]
    try:
        if method == "test":
            test(AdapterInstance.from_input()).send_results()
        elif method == "endpoint_urls":
            get_endpoints(AdapterInstance.from_input()).send_results()
        elif method == "collect":
            collect(AdapterInstance.from_input()).send_results()
        elif method == "adapter_definition":
            result = get_adapter_definition()
            if type(result) is AdapterDefinition:
                result.send_results()
            else:
                logger.info(
                    "get_adapter_definition method did not return an AdapterDefinition"
                )
                exit(1)
        else:
            logger.error(f"Command {method} not found")
            exit(1)
    finally:
        logger.info(Timer.graph())


if __name__ == "__main__":
    main(sys.argv[1:])
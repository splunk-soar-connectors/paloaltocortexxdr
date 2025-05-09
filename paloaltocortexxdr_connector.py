# File: paloaltocortexxdr_connector.py
#
# Copyright (c) Cyberforce Limited, 2021-2025
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.

# Python 3 Compatibility imports

import hashlib
import json
import secrets
import string
from datetime import datetime, timedelta, timezone

# Phantom App imports
import phantom.app as phantom
import requests
from bs4 import BeautifulSoup
from phantom.action_result import ActionResult
from phantom.base_connector import BaseConnector

# Usage of the consts file is recommended
from paloaltocortexxdr_consts import *


class RetVal(tuple):
    def __new__(cls, val1, val2=None):
        return tuple.__new__(RetVal, (val1, val2))


class TestConnector(BaseConnector):
    def __init__(self):
        # Call the BaseConnectors init first
        super().__init__()

        self._state = None

        # Variable to hold a base_url in case the app makes REST calls
        # Do note that the app json defines the asset config, so please
        # modify this as you deem fit.
        self._base_url = None
        self._api_key = None
        self._advanced = None
        self._api_key_id = None

    def _get_error_message_from_exception(self, e):
        """This method is used to get appropriate error messages from the exception.
        :param e: Exception object
        :return: error message
        """

        try:
            if e.args:
                if len(e.args) > 1:
                    err_code = e.args[0]
                    err_msg = e.args[1]
                elif len(e.args) == 1:
                    err_code = ERR_CODE_MSG
                    err_msg = e.args[0]
            else:
                err_code = ERR_CODE_MSG
                err_msg = ERR_MSG_UNAVAILABLE
        except:
            err_code = ERR_CODE_MSG
            err_msg = ERR_MSG_UNAVAILABLE

        try:
            if err_code in ERR_CODE_MSG:
                err_text = f"Error Message: {err_msg}"
            else:
                err_text = f"Error Code: {err_code}. Error Message: {err_msg}"
        except:
            self.debug_print(PARSE_ERR_MSG)
            err_text = PARSE_ERR_MSG

        return err_text

    def _validate_integer(self, action_result, parameter, key):
        if parameter is not None:
            try:
                if not float(parameter).is_integer():
                    return action_result.set_status(phantom.APP_ERROR, VALID_INTEGER_MSG.format(key=key)), None

                parameter = int(parameter)
            except:
                return action_result.set_status(phantom.APP_ERROR, VALID_INTEGER_MSG.format(key=key)), None

            if parameter < 0:
                return action_result.set_status(phantom.APP_ERROR, NON_NEGATIVE_INTEGER_MSG.format(key=key)), None

        return phantom.APP_SUCCESS, parameter

    def _process_empty_response(self, response, action_result):
        if response.status_code == 200:
            return RetVal(phantom.APP_SUCCESS, {})

        return RetVal(
            action_result.set_status(phantom.APP_ERROR, f"Status code: {response.status_code}. Empty response and no information in the header"),
            None,
        )

    def _process_html_response(self, response, action_result):
        # An html response, treat it like an error
        status_code = response.status_code

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            for element in soup(["script", "style", "footer", "nav"]):
                element.extract()
            error_text = soup.text
            split_lines = error_text.split("\n")
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = "\n".join(split_lines)
        except:
            error_text = "Cannot parse error details"

        message = f"Status Code: {status_code}. Data from server:\n{error_text}\n"

        message = message.replace("{", "{{").replace("}", "}}")
        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_json_response(self, r, action_result):
        # Try a json parse
        try:
            resp_json = r.json()
        except Exception as e:
            err = self._get_error_message_from_exception(e)
            error_message = f"Unable to parse JSON response. Error: {err}"
            return RetVal(action_result.set_status(phantom.APP_ERROR, error_message), None)

        # Please specify the status codes here
        if 200 <= r.status_code < 399:
            return RetVal(phantom.APP_SUCCESS, resp_json)

        # You should process the error returned in the json
        error_message = r.text.replace("{", "{{").replace("}", "}}")
        message = f"Error from server. Status Code: {r.status_code} Data from server: {error_message}"

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_response(self, r, action_result):
        # store the r_text in debug data, it will get dumped in the logs if the action fails
        if hasattr(action_result, "add_debug_data"):
            action_result.add_debug_data({"r_status_code": r.status_code})
            action_result.add_debug_data({"r_text": r.text})
            action_result.add_debug_data({"r_headers": r.headers})

        # Process each 'Content-Type' of response separately

        # Process a json response
        if "json" in r.headers.get("Content-Type", ""):
            return self._process_json_response(r, action_result)

        # Process an HTML response, Do this no matter what the api talks.
        # There is a high chance of a PROXY in between phantom and the rest of
        # world, in case of errors, PROXY's return HTML, this function parses
        # the error and adds it to the action_result.
        if "html" in r.headers.get("Content-Type", ""):
            return self._process_html_response(r, action_result)

        # it's not content-type that is to be parsed, handle an empty response
        if not r.text:
            return self._process_empty_response(r, action_result)

        # everything else is actually an error at this point
        message = "Can't process response from server. Status Code: {} Data from server: {}".format(
            r.status_code, r.text.replace("{", "{{").replace("}", "}}")
        )

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _make_rest_call(self, endpoint, action_result, method="post", **kwargs):
        # **kwargs can be any additional parameters that requests.request accepts
        resp_json = None

        try:
            request_func = getattr(requests, method)
        except AttributeError:
            return RetVal(action_result.set_status(phantom.APP_ERROR, f"Invalid method: {method}"), resp_json)

        # Create a URL to connect to
        url = f"{self._base_url}{endpoint}"

        try:
            r = request_func(url, verify=self._verify, **kwargs)
        except requests.exceptions.InvalidURL:
            error_message = f"Error connecting to server. Invalid URL {url}"
            return RetVal(action_result.set_status(phantom.APP_ERROR, error_message), resp_json)
        except requests.exceptions.ConnectionError:
            error_message = f"Error connecting to server. Connection Refused from the Server for {url}"
            return RetVal(action_result.set_status(phantom.APP_ERROR, error_message), resp_json)
        except requests.exceptions.InvalidSchema:
            error_message = f"Error connecting to server. No connection adapters were found for {url}"
            return RetVal(action_result.set_status(phantom.APP_ERROR, error_message), resp_json)
        except Exception as e:
            err = self._get_error_message_from_exception(e)
            error_message = f"Error Connecting to server. {err}"
            return RetVal(action_result.set_status(phantom.APP_ERROR, error_message), resp_json)

        return self._process_response(r, action_result)

    def authenticationHeaders(self):
        if self._advanced:
            # Generate a 64 bytes random string
            nonce = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))
            # Get the current timestamp as milliseconds
            timestamp = int(datetime.now(timezone.utc).timestamp()) * 1000
            # Generate the auth key
            auth_key = f"{self._api_key}{nonce}{timestamp}"
            # Convert to bytes object
            auth_key = auth_key.encode("utf-8")
            # Calculate sha256
            api_key_hash = hashlib.sha256(auth_key).hexdigest()
            headers = {
                "x-xdr-timestamp": str(timestamp),
                "x-xdr-nonce": nonce,
                "x-xdr-auth-id": str(self._api_key_id),
                "Authorization": api_key_hash,
            }
        else:
            headers = {"x-xdr-auth-id": str(self._api_key_id), "Authorization": self._api_key}

        return headers

    def _handle_on_poll(self, param):
        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        polled_count = 0
        incidents = []

        while True:
            obj, sort, request_data, parameters = {}, {}, {}, {}
            filters = []
            obj["field"] = "creation_time"
            obj["operator"] = "gte"
            obj["value"] = self._state.get("last_incident", int((datetime.now(timezone.utc) - timedelta(days=7)).timestamp() * 1000))
            filters.append(obj)
            request_data["filters"] = filters
            sort["field"] = "creation_time"
            sort["keyword"] = "asc"
            request_data["sort"] = sort
            parameters["request_data"] = request_data

            # make rest call
            headers = self.authenticationHeaders()
            ret_val, response = self._make_rest_call("/incidents/get_incidents/", action_result, headers=headers, json=parameters)

            if phantom.is_fail(ret_val):
                # the call to the 3rd party device or service failed, action result should contain all the error details
                return action_result.get_status()

            reply = response["reply"]
            if reply["total_count"] == 0:
                break
            polled_count += reply["result_count"]
            incidents += reply["incidents"]
            self._state.update({"last_incident": incidents[-1]["creation_time"] + 1})
            self.save_state(self._state)

            if reply["total_count"] == reply["result_count"]:
                break

        for incident in incidents:
            cef, container = {}, {}
            container["name"] = "Cortex XDR Incident {}".format(incident["incident_id"])
            container["description"] = "Cortex XDR Incident"

            first_cef = True

            for key, value in incident.items():
                if first_cef:
                    cef["cortex_xdr"] = True
                    first_cef = False
                cef[key] = value
                artifacts = []
                artifact = {"label": "incident", "cef": cef}
                artifacts.append(artifact)
                container["data"] = incident
                container["artifacts"] = artifacts

            status, message, container_id = self.save_container(container)
            if status == phantom.APP_ERROR:
                self.debug_print(f"Failed to store: {message}")
                self.debug_print(f"stat/msg {status}/{message}")
                return action_result.set_status(phantom.APP_ERROR, f"Container creation failed: {message}")

        # Return success
        self.save_progress(f"{polled_count} incident(s) polled")
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_test_connectivity(self, param):
        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        self.save_progress("Connecting to API server")

        # make rest call
        headers = self.authenticationHeaders()
        parameters = {}
        ret_val, response = self._make_rest_call("/endpoints/get_endpoints/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            self.save_progress("Test Connectivity Failed")
            return action_result.get_status()

        # Return success
        self.save_progress("Test Connectivity Passed")
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_list_endpoints(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        parameters = {}
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/endpoints/get_endpoints/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            reply = response["reply"]
            summary["endpoint_count"] = str(len(reply))
            for x in range(len(reply)):
                summary[f"endpoint_{x + 1}"] = reply[x]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_get_policy(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary
        endpoint_id = param["endpoint_id"]

        request_data, parameters = {}, {}
        request_data["endpoint_id"] = endpoint_id
        parameters["request_data"] = request_data
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/endpoints/get_policy/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            reply = response["reply"]
            summary["policy_name"] = reply["policy_name"]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_get_action_status(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary
        action_id = param["action_id"]
        # Validate 'action_id' action parameter
        ret_val, action_id = self._validate_integer(action_result, action_id, ACTIONID_ACTION_PARAM)
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        request_data, parameters = {}, {}
        request_data["group_action_id"] = action_id
        parameters["request_data"] = request_data
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/actions/get_action_status/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            reply = response["reply"]
            summary["action_status"] = reply["data"]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_retrieve_file(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary
        endpoint_id = param["endpoint_id"]
        files_windows = param.get("windows_path")
        files_linux = param.get("linux_path")
        files_macos = param.get("macos_path")

        obj, files, request_data, parameters = {}, {}, {}, {}
        endpoints, filters = [], []
        endpoints.append(endpoint_id)
        obj["field"] = "endpoint_id_list"
        obj["operator"] = "in"
        obj["value"] = endpoints
        filters.append(obj)
        request_data["filters"] = filters
        if files_windows:
            windows = []
            windows.append(files_windows)
            files["windows"] = windows
        if files_linux:
            linux = []
            linux.append(files_linux)
            files["linux"] = linux
        if files_macos:
            macos = []
            macos.append(files_macos)
            files["macos"] = macos
        if not files:
            return action_result.set_status(phantom.APP_ERROR, "Please provide at least one file path")
        request_data["files"] = files
        parameters["request_data"] = request_data
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/endpoints/file_retrieval/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            reply = response["reply"]
            summary["action_id"] = reply["action_id"]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_retrieve_file_details(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary
        action_id = param["action_id"]
        # Validate 'action_id' action parameter
        ret_val, action_id = self._validate_integer(action_result, action_id, ACTIONID_ACTION_PARAM)
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        request_data, parameters = {}, {}
        request_data["group_action_id"] = action_id
        parameters["request_data"] = request_data
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/actions/file_retrieval_details/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            reply = response["reply"]
            summary["file_url"] = reply["data"]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_quarantine_file(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary
        endpoint_id = param["endpoint_id"]
        file_path = param["file_path"]
        file_hash = param["file_hash"]

        obj, request_data, parameters = {}, {}, {}
        endpoints, filters = [], []
        endpoints.append(endpoint_id)
        obj["field"] = "endpoint_id_list"
        obj["operator"] = "in"
        obj["value"] = endpoints
        filters.append(obj)
        request_data["filters"] = filters
        request_data["file_path"] = file_path
        request_data["file_hash"] = file_hash
        parameters["request_data"] = request_data
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/endpoints/quarantine/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            reply = response["reply"]
            summary["action_id"] = reply["action_id"]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_unquarantine_file(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary
        file_hash = param["file_hash"]
        endpoint_id = param["endpoint_id"]

        request_data, parameters = {}, {}
        request_data["file_hash"] = file_hash
        request_data["endpoint_id"] = endpoint_id
        parameters["request_data"] = request_data
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/endpoints/restore/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            reply = response["reply"]
            summary["action_id"] = reply["action_id"]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_block_hash(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary
        file_hash = param["file_hash"]
        comment = param.get("comment")
        incident_id = param.get("incident_id")

        request_data, parameters = {}, {}
        request_data["hash_list"] = [file_hash]
        if comment:
            request_data["comment"] = comment
        if incident_id:
            # Validate 'incident_id' action parameter
            ret_val, incident_id = self._validate_integer(action_result, incident_id, INCIDENTID_ACTION_PARAM)
            if phantom.is_fail(ret_val):
                return action_result.get_status()
            request_data["incident_id"] = str(incident_id)

        parameters["request_data"] = request_data
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/hash_exceptions/blocklist/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            summary["list_updated"] = response["reply"]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_allow_hash(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary
        file_hash = param["file_hash"]
        comment = param.get("comment")
        incident_id = param.get("incident_id")

        request_data, parameters = {}, {}
        request_data["hash_list"] = [file_hash]
        if comment:
            request_data["comment"] = comment
        if incident_id:
            # Validate 'incident_id' action parameter
            ret_val, incident_id = self._validate_integer(action_result, incident_id, INCIDENTID_ACTION_PARAM)
            if phantom.is_fail(ret_val):
                return action_result.get_status()
            request_data["incident_id"] = str(incident_id)

        parameters["request_data"] = request_data
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/hash_exceptions/allowlist/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            summary["list_updated"] = response["reply"]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_quarantine_device(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary
        endpoint_id = param["endpoint_id"]

        request_data, parameters = {}, {}
        request_data["endpoint_id"] = endpoint_id
        parameters["request_data"] = request_data
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/endpoints/isolate/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            reply = response["reply"]
            summary["action_id"] = reply["action_id"]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_unquarantine_device(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary
        endpoint_id = param["endpoint_id"]

        request_data, parameters = {}, {}
        request_data["endpoint_id"] = endpoint_id
        parameters["request_data"] = request_data
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/endpoints/unisolate/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            reply = response["reply"]
            summary["action_id"] = reply["action_id"]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_scan_endpoint(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary
        scan_all = param.get("scan_all", False)
        endpoint_id = param.get("endpoint_id")
        dist_name = param.get("dist_name")
        first_seen = param.get("first_seen")
        last_seen = param.get("last_seen")
        ip_list = param.get("ip_list")
        group_name = param.get("group_name")
        platform = param.get("platform")
        alias = param.get("alias")
        isolated = param.get("isolated")
        unisolated = param.get("unisolated")
        hostname = param.get("hostname")
        scan_status = param.get("scan_status")

        request_data, parameters = {}, {}
        if scan_all:
            request_data["filters"] = "all"
        else:
            filters = []
            if endpoint_id:
                endpoints = []
                obj = {}
                endpoints.append(endpoint_id)
                obj["field"] = "endpoint_id_list"
                obj["operator"] = "in"
                obj["value"] = endpoints
                filters.append(obj)
            if dist_name:
                dists = []
                obj = {}
                dists.append(dist_name)
                obj["field"] = "dist_name"
                obj["operator"] = "in"
                obj["value"] = dists
                filters.append(obj)
            if first_seen:
                # Validate 'first_seen' action parameter
                ret_val, first_seen = self._validate_integer(action_result, first_seen, FIRSTSEEN_ACTION_PARAM)
                if phantom.is_fail(ret_val):
                    return action_result.get_status()
                obj = {}
                obj["field"] = "first_seen"
                obj["operator"] = "gte"
                obj["value"] = first_seen
                filters.append(obj)
            if last_seen:
                # Validate 'last_seen' action parameter
                ret_val, last_seen = self._validate_integer(action_result, last_seen, LASTSEEN_ACTION_PARAM)
                if phantom.is_fail(ret_val):
                    return action_result.get_status()
                obj = {}
                obj["field"] = "last_seen"
                obj["operator"] = "gte"
                obj["value"] = last_seen
                filters.append(obj)
            if ip_list:
                ips = []
                obj = {}
                ips.append(ip_list)
                obj["field"] = "ip_list"
                obj["operator"] = "in"
                obj["value"] = ips
                filters.append(obj)
            if group_name:
                groups = []
                obj = {}
                groups.append(group_name)
                obj["field"] = "group_name"
                obj["operator"] = "in"
                obj["value"] = groups
                filters.append(obj)
            if platform:
                if any(value == platform for value in PLATFORMS_LIST):
                    temp = []
                    obj = {}
                    temp.append(platform)
                    obj["field"] = "platform"
                    obj["operator"] = "in"
                    obj["value"] = temp
                    filters.append(obj)
                else:
                    return action_result.set_status(phantom.APP_ERROR, VALID_VALUE_MSG.format(key=PLATFORM_ACTION_PARAM))
            if alias:
                aliases = []
                obj = {}
                aliases.append(alias)
                obj["field"] = "alias"
                obj["operator"] = "in"
                obj["value"] = aliases
                filters.append(obj)
            if isolated:
                isolates = []
                obj = {}
                isolates.append("isolated")
                obj["field"] = "isolate"
                obj["operator"] = "in"
                obj["value"] = isolates
                filters.append(obj)
            if unisolated:
                isolates = []
                obj = {}
                isolates.append("unisolated")
                obj["field"] = "isolate"
                obj["operator"] = "in"
                obj["value"] = isolates
                filters.append(obj)
            if hostname:
                hostnames = []
                obj = {}
                hostnames.append(hostname)
                obj["field"] = "hostname"
                obj["operator"] = "in"
                obj["value"] = hostnames
                filters.append(obj)
            if scan_status:
                if any(value == scan_status for value in SCAN_STATUSES):
                    status = []
                    obj = {}
                    status.append(scan_status)
                    obj["field"] = "scan_status"
                    obj["operator"] = "in"
                    obj["value"] = status
                    filters.append(obj)
                else:
                    return action_result.set_status(phantom.APP_ERROR, VALID_VALUE_MSG.format(key=SCANSTATUS_ACTION_PARAM))
            if not filters:
                return action_result.set_status(phantom.APP_ERROR, "Please provide at least one filter criterion")
            request_data["filters"] = filters

        parameters["request_data"] = request_data
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/endpoints/scan/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            reply = response["reply"]
            summary["action_id"] = reply["action_id"]
            summary["endpoint_scanning"] = reply["endpoints_count"]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_cancel_scan_endpoint(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary
        scan_all = param.get("scan_all", False)
        endpoint_id = param.get("endpoint_id")
        dist_name = param.get("dist_name")
        first_seen = param.get("first_seen")
        last_seen = param.get("last_seen")
        ip_list = param.get("ip_list")
        group_name = param.get("group_name")
        platform = param.get("platform")
        alias = param.get("alias")
        isolated = param.get("isolated")
        unisolated = param.get("unisolated")
        hostname = param.get("hostname")
        scan_status = param.get("scan_status")

        request_data, parameters = {}, {}
        if scan_all:
            request_data["filters"] = "all"
        else:
            filters = []
            if endpoint_id:
                endpoints = []
                obj = {}
                endpoints.append(endpoint_id)
                obj["field"] = "endpoint_id_list"
                obj["operator"] = "in"
                obj["value"] = endpoints
                filters.append(obj)
            if dist_name:
                dists = []
                obj = {}
                dists.append(dist_name)
                obj["field"] = "dist_name"
                obj["operator"] = "in"
                obj["value"] = dists
                filters.append(obj)
            if first_seen:
                # Validate 'first_seen' action parameter
                ret_val, first_seen = self._validate_integer(action_result, first_seen, FIRSTSEEN_ACTION_PARAM)
                if phantom.is_fail(ret_val):
                    return action_result.get_status()
                obj = {}
                obj["field"] = "first_seen"
                obj["operator"] = "gte"
                obj["value"] = first_seen
                filters.append(obj)
            if last_seen:
                # Validate 'last_seen' action parameter
                ret_val, last_seen = self._validate_integer(action_result, last_seen, LASTSEEN_ACTION_PARAM)
                if phantom.is_fail(ret_val):
                    return action_result.get_status()
                obj = {}
                obj["field"] = "last_seen"
                obj["operator"] = "gte"
                obj["value"] = last_seen
                filters.append(obj)
            if ip_list:
                ips = []
                obj = {}
                ips.append(ip_list)
                obj["field"] = "ip_list"
                obj["operator"] = "in"
                obj["value"] = ips
                filters.append(obj)
            if group_name:
                groups = []
                obj = {}
                groups.append(group_name)
                obj["field"] = "group_name"
                obj["operator"] = "in"
                obj["value"] = groups
                filters.append(obj)
            if platform:
                if any(value == platform for value in PLATFORMS_LIST):
                    temp = []
                    obj = {}
                    temp.append(platform)
                    obj["field"] = "platform"
                    obj["operator"] = "in"
                    obj["value"] = temp
                    filters.append(obj)
                else:
                    return action_result.set_status(phantom.APP_ERROR, VALID_VALUE_MSG.format(key=PLATFORM_ACTION_PARAM))
            if alias:
                aliases = []
                obj = {}
                aliases.append(alias)
                obj["field"] = "alias"
                obj["operator"] = "in"
                obj["value"] = aliases
                filters.append(obj)
            if isolated:
                isolates = []
                obj = {}
                isolates.append("isolated")
                obj["field"] = "isolate"
                obj["operator"] = "in"
                obj["value"] = isolates
                filters.append(obj)
            if unisolated:
                isolates = []
                obj = {}
                isolates.append("unisolated")
                obj["field"] = "isolate"
                obj["operator"] = "in"
                obj["value"] = isolates
                filters.append(obj)
            if hostname:
                hostnames = []
                obj = {}
                hostnames.append(hostname)
                obj["field"] = "hostname"
                obj["operator"] = "in"
                obj["value"] = hostnames
                filters.append(obj)
            if scan_status:
                if any(value == scan_status for value in SCAN_STATUSES):
                    status = []
                    obj = {}
                    status.append(scan_status)
                    obj["field"] = "scan_status"
                    obj["operator"] = "in"
                    obj["value"] = status
                    filters.append(obj)
                else:
                    return action_result.set_status(phantom.APP_ERROR, VALID_VALUE_MSG.format(key=SCANSTATUS_ACTION_PARAM))
            if not filters:
                return action_result.set_status(phantom.APP_ERROR, "Please provide at least one filter criterion")
            request_data["filters"] = filters

        parameters["request_data"] = request_data
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/endpoints/abort_scan/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            reply = response["reply"]
            summary["action_id"] = reply["action_id"]
            summary["endpoint_cancelling"] = reply["endpoints_count"]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_get_incidents(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        self._state.update({"last_incident": 1000000000000})

        # Access action parameters passed in the 'param' dictionary
        modification_time = param.get("modification_time")
        creation_time = param.get("creation_time")
        incident_id = param.get("incident_id")
        description = param.get("description")
        alert_sources = param.get("alert_sources")
        status = param.get("status")
        search_from = param.get("search_from")
        search_to = param.get("search_to")
        sort = param.get("sort", False)
        sort_field = param.get("sort_field", "creation_time")
        sort_order = param.get("sort_order", "desc")

        request_data, parameters = {}, {}
        filters = []
        if modification_time:
            # Validate 'modification_time' action parameter
            ret_val, modification_time = self._validate_integer(action_result, modification_time, MODIFICATIONTIME_ACTION_PARAM)
            if phantom.is_fail(ret_val):
                return action_result.get_status()
            obj = {}
            obj["field"] = "modification_time"
            obj["operator"] = "gte"
            obj["value"] = modification_time
            filters.append(obj)
        if creation_time:
            # Validate 'creation_time' action parameter
            ret_val, creation_time = self._validate_integer(action_result, creation_time, CREATIONTIME_ACTION_PARAM)
            if phantom.is_fail(ret_val):
                return action_result.get_status()
            obj = {}
            obj["field"] = "creation_time"
            obj["operator"] = "gte"
            obj["value"] = creation_time
            filters.append(obj)
        if incident_id:
            # Validate 'incident_id' action parameter
            ret_val, incident_id = self._validate_integer(action_result, incident_id, INCIDENTID_ACTION_PARAM)
            if phantom.is_fail(ret_val):
                return action_result.get_status()
            incidents = []
            obj = {}
            incidents.append(str(incident_id))
            obj["field"] = "incident_id_list"
            obj["operator"] = "in"
            obj["value"] = incidents
            filters.append(obj)
        if description:
            obj = {}
            obj["field"] = "description"
            obj["operator"] = "contains"
            obj["value"] = description
            filters.append(obj)
        if alert_sources:
            sources = []
            obj = {}
            sources.append(alert_sources)
            obj["field"] = "alert_sources_list"
            obj["operator"] = "in"
            obj["value"] = sources
            filters.append(obj)
        if status:
            statuses = [
                "new",
                "under_investigation",
                "resolved_threat_handled",
                "resolved_known_issue",
                "resolved_false_positive",
                "resolved_other",
                "resolved_auto",
            ]
            if any(value == status for value in statuses):
                obj = {}
                obj["field"] = "status"
                obj["operator"] = "eq"
                obj["value"] = status
                filters.append(obj)
            else:
                return action_result.set_status(phantom.APP_ERROR, VALID_VALUE_MSG.format(key=STATUS_ACTION_PARAM))
        if filters:
            request_data["filters"] = filters
        if search_from:
            # Validate 'search_from' action parameter
            ret_val, search_from = self._validate_integer(action_result, search_from, SEARCHFROM_ACTION_PARAM)
            if phantom.is_fail(ret_val):
                return action_result.get_status()
            request_data["search_from"] = search_from
        if search_to:
            # Validate 'search_to' action parameter
            ret_val, search_to = self._validate_integer(action_result, search_to, SEARCHTO_ACTION_PARAM)
            if phantom.is_fail(ret_val):
                return action_result.get_status()
            request_data["search_to"] = search_to
        if sort:
            fields = ["modification_time", "creation_time"]
            if any(value == sort_field for value in fields):
                if any(value == sort_order for value in SORT_ORDERS):
                    sorting = {}
                    sorting["field"] = sort_field
                    sorting["keyword"] = sort_order
                    request_data["sort"] = sorting
                else:
                    return action_result.set_status(phantom.APP_ERROR, VALID_VALUE_MSG.format(key=SORTORDER_ACTION_PARAM))
            else:
                return action_result.set_status(phantom.APP_ERROR, VALID_VALUE_MSG.format(key=SORTFIELD_ACTION_PARAM))
        parameters["request_data"] = request_data
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/incidents/get_incidents/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            reply = response["reply"]
            summary["total_count"] = reply["total_count"]
            summary["result_count"] = reply["result_count"]
            incidents = reply["incidents"]
            for x in range(len(incidents)):
                summary[f"result_{x + 1}"] = incidents[x]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_get_incident_details(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary
        incident_id = param["incident_id"]
        alerts_limit = param.get("alerts_limit")

        request_data, parameters = {}, {}
        # Validate 'incident_id' action parameter
        ret_val, incident_id = self._validate_integer(action_result, incident_id, INCIDENTID_ACTION_PARAM)
        if phantom.is_fail(ret_val):
            return action_result.get_status()
        request_data["incident_id"] = str(incident_id)
        if alerts_limit:
            # Validate 'alerts_limit' action parameter
            ret_val, alerts_limit = self._validate_integer(action_result, alerts_limit, ALERTSLIMIT_ACTION_PARAM)
            if phantom.is_fail(ret_val):
                return action_result.get_status()
            request_data["alerts_limit"] = alerts_limit
        parameters["request_data"] = request_data
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/incidents/get_incident_extra_data/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            reply = response["reply"]["file_artifacts"]["data"][0]
            summary["alert_count"] = reply["alert_count"]
            summary["is_malicious"] = reply["is_malicious"]
            summary["file_name"] = reply["file_name"]
            summary["file_sha256"] = reply["file_sha256"]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_get_alerts(self, param):
        # use self.save_progress(...) to send progress messages back to the platform
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Access action parameters passed in the 'param' dictionary
        alert_id = param.get("alert_id")
        alert_source = param.get("alert_source")
        severity = param.get("severity")
        creation_time = param.get("creation_time")
        search_from = param.get("search_from")
        search_to = param.get("search_to")
        sort = param.get("sort", False)
        sort_field = param.get("sort_field", "creation_time")
        sort_order = param.get("sort_order", "desc")

        request_data, parameters = {}, {}
        filters = []
        if alert_id:
            # Validate 'alert_id' action parameter
            ret_val, alert_id = self._validate_integer(action_result, alert_id, ALERTID_ACTION_PARAM)
            if phantom.is_fail(ret_val):
                return action_result.get_status()
            alerts = []
            obj = {}
            alerts.append(alert_id)
            obj["field"] = "alert_id_list"
            obj["operator"] = "in"
            obj["value"] = alerts
            filters.append(obj)
        if alert_source:
            sources = []
            obj = {}
            sources.append(alert_source)
            obj["field"] = "alert_source"
            obj["operator"] = "in"
            obj["value"] = sources
            filters.append(obj)
        if severity:
            severities = ["info", "low", "medium", "high", "unknown"]
            if any(value == severity for value in severities):
                temp = []
                obj = {}
                temp.append(severity)
                obj["field"] = "severity"
                obj["operator"] = "in"
                obj["value"] = temp
                filters.append(obj)
            else:
                return action_result.set_status(phantom.APP_ERROR, VALID_VALUE_MSG.format(key=SEVERITY_ACTION_PARAM))
        if creation_time:
            # Validate 'creation_time' action parameter
            ret_val, creation_time = self._validate_integer(action_result, creation_time, CREATIONTIME_ACTION_PARAM)
            if phantom.is_fail(ret_val):
                return action_result.get_status()
            obj = {}
            obj["field"] = "creation_time"
            obj["operator"] = "gte"
            obj["value"] = creation_time
            filters.append(obj)
        if filters:
            request_data["filters"] = filters
        if search_from:
            # Validate 'search_from' action parameter
            ret_val, search_from = self._validate_integer(action_result, search_from, SEARCHFROM_ACTION_PARAM)
            if phantom.is_fail(ret_val):
                return action_result.get_status()
            request_data["search_from"] = search_from
        if search_to:
            # Validate 'search_to' action parameter
            ret_val, search_to = self._validate_integer(action_result, search_to, SEARCHTO_ACTION_PARAM)
            if phantom.is_fail(ret_val):
                return action_result.get_status()
            request_data["search_to"] = search_to
        if sort:
            fields = ["severity", "creation_time"]
            if any(value == sort_field for value in fields):
                if any(value == sort_order for value in SORT_ORDERS):
                    sorting = {}
                    sorting["field"] = sort_field
                    sorting["keyword"] = sort_order
                    request_data["sort"] = sorting
                else:
                    return action_result.set_status(phantom.APP_ERROR, VALID_VALUE_MSG.format(key=SORTORDER_ACTION_PARAM))
            else:
                return action_result.set_status(phantom.APP_ERROR, VALID_VALUE_MSG.format(key=SORTFIELD_ACTION_PARAM))
        parameters["request_data"] = request_data
        self.save_progress(f"Request JSON: {parameters}")

        # make rest call
        headers = self.authenticationHeaders()
        ret_val, response = self._make_rest_call("/alerts/get_alerts_multi_events/", action_result, headers=headers, json=parameters)

        if phantom.is_fail(ret_val):
            # the call to the 3rd party device or service failed, action result should contain all the error details
            return action_result.get_status()

        # Add the response into the data section
        action_result.add_data(response)
        self.save_progress(f"Response JSON: {response}")

        try:
            # Add a dictionary that is made up of the most important values from data into the summary
            summary = action_result.update_summary({})
            reply = response["reply"]
            summary["total_count"] = reply["total_count"]
            summary["result_count"] = reply["result_count"]
            alerts = reply["alerts"]
            event = alerts[0]["events"]
            summary["process_name"] = event[0]["actor_process_image_name"]
            summary["process_path"] = event[0]["actor_process_image_path"]
            summary["process_sha256"] = event[0]["actor_process_image_sha256"]
            summary["endpoint_id"] = alerts[0]["endpoint_id"]
            summary["host_name"] = alerts[0]["host_name"]
            summary["ip_address"] = alerts[0]["host_ip"]
            for x in range(len(alerts)):
                summary[f"Result {x + 1}"] = alerts[x]
            summary["raw"] = response
        except Exception:
            self.debug_print(ERR_PARSING_RESPONSE)

        # Return success, no need to set the message, only the status
        # BaseConnector will create a textual message based off of the summary dictionary
        return action_result.set_status(phantom.APP_SUCCESS)

    def handle_action(self, param):
        ret_val = phantom.APP_SUCCESS

        # Get the action that we are supposed to execute for this App Run
        action_id = self.get_action_identifier()

        self.debug_print("action_id", self.get_action_identifier())

        if action_id == "on_poll":
            ret_val = self._handle_on_poll(param)

        elif action_id == "test_connectivity":
            ret_val = self._handle_test_connectivity(param)

        elif action_id == "list_endpoints":
            ret_val = self._handle_list_endpoints(param)

        elif action_id == "get_policy":
            ret_val = self._handle_get_policy(param)

        elif action_id == "get_action_status":
            ret_val = self._handle_get_action_status(param)

        elif action_id == "retrieve_file":
            ret_val = self._handle_retrieve_file(param)

        elif action_id == "retrieve_file_details":
            ret_val = self._handle_retrieve_file_details(param)

        elif action_id == "quarantine_file":
            ret_val = self._handle_quarantine_file(param)

        elif action_id == "unquarantine_file":
            ret_val = self._handle_unquarantine_file(param)

        elif action_id == "block_hash":
            ret_val = self._handle_block_hash(param)

        elif action_id == "allow_hash":
            ret_val = self._handle_allow_hash(param)

        elif action_id == "quarantine_device":
            ret_val = self._handle_quarantine_device(param)

        elif action_id == "unquarantine_device":
            ret_val = self._handle_unquarantine_device(param)

        elif action_id == "scan_endpoint":
            ret_val = self._handle_scan_endpoint(param)

        elif action_id == "cancel_scan_endpoint":
            ret_val = self._handle_cancel_scan_endpoint(param)

        elif action_id == "get_incidents":
            ret_val = self._handle_get_incidents(param)

        elif action_id == "get_incident_details":
            ret_val = self._handle_get_incident_details(param)

        elif action_id == "get_alerts":
            ret_val = self._handle_get_alerts(param)

        return ret_val

    def initialize(self):
        # Load the state in initialize, use it to store data
        # that needs to be accessed across actions
        self._state = self.load_state()

        # get the asset config
        config = self.get_config()

        self._base_url = "https://api-{}/public_api/v1".format(config["fqdn"])
        self._api_key = config["api_key"]
        self._advanced = config.get("advanced", False)
        self._api_key_id = config["api_id"]
        self._verify = config.get("verify_server_cert", False)

        return phantom.APP_SUCCESS

    def finalize(self):
        # Save the state, this data is saved across actions and app upgrades
        self.save_state(self._state)
        return phantom.APP_SUCCESS


def main():
    import argparse
    import sys

    import pudb

    pudb.set_trace()

    argparser = argparse.ArgumentParser()

    argparser.add_argument("input_test_json", help="Input Test JSON file")
    argparser.add_argument("-u", "--username", help="username", required=False)
    argparser.add_argument("-p", "--password", help="password", required=False)
    argparser.add_argument("-v", "--verify", action="store_true", help="verify", required=False, default=False)

    args = argparser.parse_args()
    session_id = None

    username = args.username
    password = args.password
    verify = args.verify

    if username is not None and password is None:
        # User specified a username but not a password, so ask
        import getpass

        password = getpass.getpass("Password: ")

    if username and password:
        try:
            login_url = BaseConnector._get_phantom_base_url() + "/login"

            print("Accessing the Login page")
            r = requests.get(login_url, verify=verify)
            csrftoken = r.cookies["csrftoken"]

            data = dict()
            data["username"] = username
            data["password"] = password
            data["csrfmiddlewaretoken"] = csrftoken

            headers = dict()
            headers["Cookie"] = "csrftoken=" + csrftoken
            headers["Referer"] = login_url

            print("Logging into Platform to get the session id")
            r2 = requests.post(login_url, verify=verify, data=data, headers=headers)
            session_id = r2.cookies["sessionid"]
        except Exception as e:
            print("Unable to get session id from the platform. Error: " + str(e))
            sys.exit(1)

    with open(args.input_test_json) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = TestConnector()
        connector.print_progress_message = True

        if session_id is not None:
            in_json["user_session_token"] = session_id
            connector._set_csrf_info(csrftoken, headers["Referer"])

        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    sys.exit(0)


if __name__ == "__main__":
    main()

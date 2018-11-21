from datetime import datetime, timedelta
import json
import logging

from velocloud.rest import ApiException
from velocloud import ApiClient, AllApi
from api.utils import serialize_json
from settings import (
    HOST,
    ENTERPRISE_ID,
    ENTERPRISE_PASSWORD,
    ENTERPRISE_USERNAME,
    OPERATOR_USERNAME,
    OPERATOR_PASSWORD,
    DEFAULT_TIME_DELTA,
    EVENT_LOG_FILE,
    FIREWALL_LOG_FILE,
    ALERT_LOG_FILE,
    TIME_FILE,
)


class VelocloudApi:
    """ Base class for the Velocloud API

    This class serves as a wrapper for the Velocloud SDK. This should
    be subclassed for each API endpoint you wish to hit.

    Args:
        client (obj): velocloud.velocloud.ApiClient used to connect to
            the Velocloud API
        time_file (str): absolute path to file that stores the last
            log's time string.
    """

    def __init__(self):
        self.client = ApiClient(host=HOST)
        self.last_time = None
        self.time_file = TIME_FILE
        self.time_format = "%Y-%m-%dT%H:%M:%S.000Z"
        self.log_file = {
            "events": EVENT_LOG_FILE,
            "firewall": FIREWALL_LOG_FILE,
            "alerts": ALERT_LOG_FILE,
        }
        self.time_keys = {
            "events": "eventTime",
            "firewall": "timestamp",
            "alerts": "created",
        }

    def _default_time_range(self, start=None):
        """ Generates a time window to search for logs based on the
        configuration defaults.

        Returns:
            start (str): Epoch of the 'start' time of the logs we're
                looking for.
            end (int): Epoch of the 'end' time of the logs we're
                looking for.
        """

        _end = datetime.now()
        if not start:
            _start = _end - timedelta(seconds=DEFAULT_TIME_DELTA)
            start = _start.strftime(self.time_format)
        end = _end.strftime(self.time_format)
        self.last_time = end
        return start, end

    def write_to_file(self, log_file, list_of_items):
        """ Writes a list of items to file.

        Args:
            log_file (str): Absolute path to log file that will be
                written to.
            list_of_items (list): List of log items to be written to
                file.
        """

        with open(log_file, "a+") as wf:
            for item in list_of_items:
                json_string = json.dumps(item)
                wf.write("{}\n".format(json_string))
        list_length_string = str(len(list_of_items))
        logging.info("Wrote {} logs to {}.".format(list_length_string, log_file))

    def time_string_to_datetime(self, time_string):
        """ Helper function to convert time string to datetime object.
        """

        return datetime.strptime(time_string, self.time_format)


class VelocloudEnterpriseApi(VelocloudApi):
    """ Velocloud SDK wrapper for Enterprise events

    Attributes:
        api (object): velocloud.velocloud.AllApi
        log_file (str): Absolute path to the log file for Enterprise
            events.
    """

    def __init__(self):
        super().__init__()
        self.client.authenticate(
            ENTERPRISE_USERNAME, ENTERPRISE_PASSWORD, operator=False
        )
        self.api = AllApi(self.client)

    def get_logs(self, start=None, end=None, type_="events"):
        """ Method to orchestrate pulling and writing firewall logs.

        Args:
            start (str): Start time of the logs we want to pull.
            end (str): End time of the logs we want to pull.
        """
        logging.info("Getting logs for {}".format(type_))
        log_list = self._get_logs_from_velocloud(start=start, end=end, type_=type_)
        log_count = str(len(log_list))
        logging.debug("Found {} logs for type: {}.".format(log_count, type_))
        log_file = self.log_file.get(type_)
        self.write_to_file(log_file, log_list)

    def _get_logs_from_velocloud(
        self, start=None, end=None, count=0, body=None, type_="events"
    ):
        """ Recursive method to call and pull down firewall logs
        from the Velocloud API.

        If the response contians metaData where 'more' == True, then
        the function will make another call to pull down the remainder
        of the logs.  Velocloud returns logs most recent to earliest.
        So on subsequent calls to the api to retrieve remaining logs,
        the function leaves the 'start' time the same, and adjusts the
        'end' time to skip the logs already acquired.

        There is potential to acquire the same log twice. For example,
        the following scenario:
            1. Earliest log returned was at 2018-11-19T18:42:23.007Z
            2. There were 5 logs at that timestamp
            3. Only two of those 5 logs fit in the last response
        In this case, our next API call would have the timestamp above
        as the 'end' time. The two logs present in the last response,
        would also be returned in the second response because they are
        still associated with that timestamp. Unfortunately, Velocloud
        has not presented a better method of pagination thus far. It
        seems that if there were 2400 logs at one particular time
        stamp, and only 2048 allowed in one response, there would be
        no way to acquire the remaining logs unless you broke it up
        into milliseconds. And even then, it depends on if the logs
        are stored with a more granular timestamp.

        Args:
            start (str): Start time.
            end (str): End time.
            count (int): The iteration of the method (increased when
                making a recursive call).
            body (dict): Data to be sent in the POST body.

        Returns:
            list: Either a list of logs from the current API call or
                a list of the current call plus all child recursive
                calls.
        """

        log_list = []
        if not body:
            body = self._build_body(start, end)
        if not count:
            self.last_time = body["interval"]["end"]
        logging.info(
            "Requestin logs for {} with interval {}".format(type_, body["interval"])
        )
        rv = self._call_api_by_type(type_=type_, body=body)
        rv_json = serialize_json(rv.to_dict(), _format=self.time_format)
        # API Errors?
        # Check for errors?
        # Key error?
        new_logs = rv_json["data"]

        # BASE CASE... there are no more more logs to pull down after
        # this response.
        if not rv_json["metaData"]["more"]:
            return new_logs

        # RECURSIVE CASE
        log_list += new_logs
        body["interval"]["end"] = self._get_earliest_timestamp(new_logs, type_=type_)
        count += 1
        log_list += self._get_logs_from_velocloud(count=count, body=body, type_=type_)
        return log_list

    def _call_api_by_type(self, type_="events", body=None):
        if type_ == "events":
            return self.api.eventGetEnterpriseEvents(body=body)
        elif type_ == "firewall":
            return self.api.firewallGetEnterpriseFirewallLogs(body=body)
        elif type_ == "alerts":
            return self.api.enterpriseGetEnterpriseAlerts(body=body)
        else:
            message = "Type {} is unexpected/unsupported.".format(type_)
            logging.error(message)
            raise ValueError(message)

    def _build_body(self, start=None, end=None):
        """ Builds the body of the POST based on config items and given
        start/end times.

        If start/end time not passed as an argument, then we default
        to the configured default time range relative to the current
        time.

        Args:
            start (int): Epoch of start time.
            end (int): Epoch of end time.

        Returns:
            dict: POST body including enterprise ID and time frame of
                desired logs.
        """

        if (not start) or (not end):
            start, end = self._default_time_range(start=start)
        body = {"enterpriseId": ENTERPRISE_ID, "interval": {"start": start, "end": end}}
        return body

    def _get_earliest_timestamp(self, event_list, type_="events"):
        """ Get the earliest event timestamp from the list of events.

        This is specifically used when making recursive API calls to
        pull back logs that were truncated in the precedening response.

        Args:
            event_list (list): Events that were pulled down from the
                preceding Velocloud API call.

        Returns:
            str: The earliest event time
        """

        earliest = None
        for event in event_list:
            try:
                time_key = self.time_keys.get(type_)
                event_time = datetime.strptime(event[time_key], self.time_format)
            except KeyError:
                message = "No valid time key found for event."
                logging.error(message)
                raise ValueError(message)
            else:
                if not earliest:
                    earliest = event_time
                    continue

                if not (event_time < earliest):
                    continue
                earliest = event_time

        return earliest.strftime(self.time_format)


class VelocloudOperatorApi(VelocloudApi):
    def __init__(self):
        super().__init__()
        self.client.authenticate(OPERATOR_USERNAME, OPERATOR_PASSWORD, operator=True)
        self.api = AllApi(self.client)

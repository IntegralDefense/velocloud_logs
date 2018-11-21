import logging

from api.base import VelocloudEnterpriseApi
from api.logging import setup_logger
from settings import LOGS_TO_PULL, SCRIPT_LOG_FILE, TIME_FILE


def read_time_from_file():
    """ Read the last run's end CTIME string """
    try:
        with open(TIME_FILE, "r") as rf:
            time_string = rf.read().strip()
    except FileNotFoundError:
        logging.error(
            "File {} not found when reading latest time stamp.".format(TIME_FILE)
        )
        return None
    else:
        logging.info("Read {} from {}".format(time_string, TIME_FILE))
        return time_string


def write_time_to_file(time_string):
    """ Write the last run's time to file """

    with open(TIME_FILE, "w+") as wf:
        wf.write(time_string)


def main():
    logging.info("Starting main function.")
    api = VelocloudEnterpriseApi()
    start_time = read_time_from_file()
    logging.info("Velocloud API object created.")
    logging.info("About to get the following log types: {}".format(LOGS_TO_PULL))
    [api.get_logs(type_=log_type, start=start_time) for log_type in LOGS_TO_PULL]
    write_time_to_file(api.last_time)


if __name__ == "__main__":
    setup_logger()
    main()
    exit()

# Velocloud Log Fetcher

A script that pulls logs down from the Velocloud Orchestrator to be ingested by a SIEM.

## Overview

This script currently pulls down Enterprise Firewall and Enterprise Event logs from the Velocloud Orchestrator for a single Enterprise ID.

After each run, the script will save the last log's timestamp to file. Upon the next run of the script, it will gather all logs from runtime back to the timestamp in the file. The script will perform recursive calls if there are too many logs for the response from Velocloud.

The logs are written to file as one JSON object per line.

You may notice that this script was put together in haste. This was due to an immediate need without the time to develop fully. With that being said, feel free to contribute as this project will be revisted from time to time as new features are required for our own use.

### Prerequisites

#### Acquire the Velocloud SDK

You must speak with your Velocloud contact and acquire the Velocloud
SDK. It is also helpful to get the SDK documentation and Swagger documentation
from your Velocloud contact as well. Once acquired, you can install the
SDK after setting up your virtual environment.

#### Gather credentials and an enterprise ID

You must have a Velocloud Enterprise user account with the appropriate permissions to read Enterprise Events and Firewall logs. Currently, the script does not support 2FA. Feel free to add support though!

You must also know the Enterprise ID for your Velocloud deployment.

### Installing

This script has not been configured to install yet, so you will have to clone directly from the github page.

1. Configure your virtual environment and then set it as your active environment.

    ```bash
    ~/velocloud$ python3 -m venv venv
    ~/velocloud$ source venv/bin/activate
    ```

2. Look in the setup.py file of the Velocloud SDK. It should contain the
commands to install the Velocloud SDK.

3. Install the rest of the requirements. You can take out the unneeded
requirements if you do not plan on performing development work (black, flake8, etc.).

    ```bash
    (venv) ~/velocloud$ pip install -r requirements.txt
    ```

4. You will want to configure your environment. Rename (or copy) the `.env.example` file to a file named `.env`.

    ```bash
    (venv) ~/velocloud$ cp .env.example .env
    ```
    OR
    ```bash
    (venv) ~/velocloud$ mv .env.example .env
    ```

5. Fill out the `.env` file contents. These key/value pairs will be used by the `settings.py` file during runtime. _Note: The operator user/pass is not supported at this time._

6. You may explore the `settings.py` file to see what other configurables there are. One important item is the `DEFAULT_TIME_DELTA` option. This determines how far back you want to pull logs. For example, if you have the `DEFAULT_TIME_DELTA` option set to 600 seconds, and if you do not have a 'time.log' file (for example: your first run of the script), then you will pull down event logs for the last ten minutes.

7. Now you may run the script

    ```bash
    (venv) ~/velocloud$ python velocloud_logs.py
    ```

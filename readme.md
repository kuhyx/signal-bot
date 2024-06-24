# Signal CLI REST API Integration Guide

This guide will help you set up and run a Signal bot using the Signal CLI REST API. For more details, refer to the [signal cli rest api examples](https://bbernhard.github.io/signal-cli-rest-api/).

## Message Formats

### Message Sent from the Same Account as the Bot

```json
{
    "envelope": {
        "source": "NAME",
        "sourceNumber": "PHONE_NUMBER",
        "sourceUuid": "SOURCE_ID",
        "sourceName": "USER_DEFINED_NAME",
        "sourceDevice": 69,
        "timestamp": 1719177728639,
        "syncMessage": {
            "sentMessage": {
                "destination": "DEST_NAME",
                "destinationNumber": "DEST_PHONE_NUMBER",
                "destinationUuid": "DEST_SEND_MESSAGE",
                "timestamp": 1719177728639,
                "message": "MESSAGE_CONTENT",
                "expiresInSeconds": 0,
                "viewOnce": false
            }
        }
    },
    "account": "BOT_ACCOUNT_PHONE_NUMBER"
}
```

### Message Sent from Another Account

```json
{
    "envelope": {
        "source": "NAME",
        "sourceNumber": "PHONE_NUMBER",
        "sourceUuid": "SOURCE_ID",
        "sourceName": "USER_DEFINED_NAME",
        "sourceDevice": 69,
        "timestamp": 1719177917717,
        "dataMessage": {
            "timestamp": 1719177917717,
            "message": "MESSAGE_CONTENT",
            "expiresInSeconds": 0,
            "viewOnce": false,
            "groupInfo": {
                "groupId": "ID_OF_GROUP_SEND_TO",
                "type": "DELIVER"
            }
        }
    },
    "account": "BOT_ACCOUNT_PHONE_NUMBER"
}
```

## Setting Up the WebSocket Server

The bot uses `asyncio` for running the WebSocket server and simple Python fetch requests/responses for sending and receiving data.

### How to Run

1. Follow the instructions on the [Signal CLI REST API GitHub page](https://github.com/bbernhard/signal-cli-rest-api#getting-started).

    The main steps are summarized below:

    ```sh
    sudo docker run -d --name signal-api --restart=always -p 9922:8080 \
        -v /home/user/signal-api:/home/.local/share/signal-cli \
        -e 'MODE=json-rpc' bbernhard/signal-cli-rest-api
    ```

2. Access the Signal CLI setup page:

    ```sh
    http://localhost:9922/v1/qrcodelink?device_name=signal-api
    ```

3. Scan the QR code to complete the Signal CLI setup.

### Clone the Repository

```sh
git clone https://github.com/kuhyx/signal-bot
```

### Initialize the Python Virtual Environment

```sh
python -m venv venv
```

### Add Necessary API Information

Edit the `venv/bin/activate` file:

```sh
vim venv/bin/activate
```

Add the following lines at the end of the file:

```sh
export PHONE_NUMBER="+69YOURPHONENUMBER"
export CAT_API="CAN_LEAVE_BLANK"
export GROUP_ID="MESSAGES_SEND_HERE_WILL_TRIGGER_COMMANDS"
export GROUP_ID_SEND="TRIGGERED_COMMANDS_WILL_SEND_DATA_HERE"
```
And source the venv shell:
```sh
source venv/bin/activate
```
### Install Required Python Packages

```sh
pip install -r requirements.txt
```

### Run the Server

```sh
python main.py
```

Now your Signal bot should be up and running, ready to send and receive messages via the Signal CLI REST API.

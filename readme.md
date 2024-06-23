Usefull:
https://bbernhard.github.io/signal-cli-rest-api/


If the message was send from the same account as the bot is connected to:
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

If the message was send from other account:
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
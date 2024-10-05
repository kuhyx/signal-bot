import os
import asyncio
import websockets
import requests
import base64
import json
from datetime import datetime, time, timedelta
# from rule34Py import rule34Py
# r34Py = rule34Py()



# Set up environment variable for the phone number
PHONE_NUMBER = os.getenv('PHONE_NUMBER', '1234567890')  # Default to '1234567890' if not set
RECEIVE_URL = f"http://localhost:9922/v1/receive/{PHONE_NUMBER}"
REMOVE_ATTACHMENT_URL = f"http://localhost:9922/v1/attachments/"
SEND_URL = 'http://localhost:9922/v2/send'
GROUP_ID = os.getenv('GROUP_ID', '')
GROUP_ID_SEND = os.getenv('GROUP_ID_SEND', '')
CAT_API = os.getenv('CAT_API', '')
last_command_time = None
warning_sent = False

class StringCounter:
    def __init__(self):
        self.string_map = {}

    async def update_string_map(self, key, common_name):
        if key in self.string_map:
            self.string_map[key]['count'] += 1
        else:
            self.string_map[key] = {'common_name': common_name, 'count': 1}
        return self.string_map

    def get_common_name(self, key):
        if key in self.string_map:
            return self.string_map[key]['common_name']
        return None

def download_image(image_url):
    # Download the image
    image_response = requests.get(image_url)
    image_response.raise_for_status()  # Ensure the request was successful
    
    # Extract the image filename from the URL
    image_filename = image_url.split("/")[-1]

    with open(image_filename, 'wb') as image_file:
        image_file.write(image_response.content)
    
    # Convert the image to base64 encoded data
    with open(image_filename, 'rb') as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    os.remove(image_filename)
    return base64_encoded_data

def fetch_and_download_image(api_url, image_url_key):
    # Send request to the API
    response = requests.get(api_url)
    response.raise_for_status()  # Ensure the request was successful
    
    # Parse the response JSON to get the image URL
    data = response.json()
    
    # Retrieve the image URL based on the provided key
    if isinstance(image_url_key, list):
        image_url = data
        for key in image_url_key:
            image_url = image_url[key]
    else:
        image_url = data[image_url_key]
    
    return download_image(image_url)

async def send_image(base64_attachments, recipients=GROUP_ID_SEND):
    data = {
        "base64_attachments": [base64_attachments],
        "number": PHONE_NUMBER,
        "recipients": [recipients]
    }
    response = requests.post(SEND_URL, json=data)
    if response.status_code == 200 or response.status_code == 201:
        print("Request was successful.")
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)

def send_message(message_content, recipients=PHONE_NUMBER):
    data = {
        "message": str(message_content),
        "number": PHONE_NUMBER,
        "recipients": [recipients]
    }
    response = requests.post(SEND_URL, json=data)
    if response.status_code == 200:
        print("Request was successful.")
    else:
        print(f"Request failed with status code: {response.status_code} {data}")
        print(response.text)


def message_message(inside_message):
    message_value = inside_message.get('message')
    return message_value

def message_group_id(inside_message):
    return inside_message.get('groupInfo', {}).get('groupId', {})

def extract_message_content(message):
    message_json = json.loads(message)
    inside_message = message_json.get('envelope', {}).get('dataMessage', {})
    if inside_message == {}:
        inside_message = message_json.get('envelope', {}).get('syncMessage', {}).get('sentMessage', {})
    return inside_message

    
def extract_source_uuid(message):
    message_json = message
    inside_message = message_json.get('sourceUuid', {})
    return inside_message

command_map = {
    ("!kot", "!koty", "!kots", "!cat", "!cats", "!meow", "!miau", "!ᴋᴏᴛ", "!𝓴𝓸𝓽", "!𝗸𝗼𝘁"): lambda recipient: send_image(fetch_and_download_image("https://api.thecatapi.com/v1/images/search", [0, 'url']), recipient),
    ("!pies", "!psy", "!dog", "!dogs", "!woof", "!szczek", "!𝗽𝗶𝗲𝘀", "!͓̽p͓̽i͓̽e͓̽s͓̽"): lambda recipient: send_image(fetch_and_download_image("https://dog.ceo/api/breeds/image/random", 'message'), recipient),
    # ("!traps"): lambda recipient: send_image(download_image(((r34Py.random_post(["trap"])).sample)), recipient)
}

def extract_source_name(message):
    message_json = message
    inside_message = message_json.get('sourceName', {})
    return inside_message


USER_MESSAGE_COUNT = {}


async def count_messages(message_content, counter):
    if message_content and should_count(message_content):
        uuid = extract_source_uuid(message_content)
        source_name = extract_source_name(message_content)
        await counter.update_string_map(uuid, source_name)
        send_message(counter.string_map, PHONE_NUMBER)


async def scheduled_task(counter):
    while True:
        now = datetime.now()
        target_time = datetime.combine(now.date(), time(21, 37))
        if now > target_time:
            target_time += timedelta(days=1)
        wait_time = (target_time - now).total_seconds()
        await asyncio.sleep(wait_time)
        # Trigger your function here
        send_message(counter.string_map, GROUP_ID_SEND)
        counter.string_map = {}

async def trigger_command(message_content, recipient):
    global last_command_time, warning_sent
    message_value = message_message(message_content)
    
    try:
        if message_value is not None and message_value[0] == "!":
            current_time = datetime.now()
            if last_command_time and current_time - last_command_time < timedelta(seconds=10):
                if not warning_sent:
                    send_message("BEEP BOOP POCZEKAJ 10 SEKUND.", recipient)
                    warning_sent = True
                return

            for command_triggers, command_function in command_map.items():
                if message_value in command_triggers:
                    await command_function(recipient)
                    last_command_time = current_time
                    warning_sent = False
                    break
    except TypeError:
        send_message(f"trigger_command, TypeError {message_content}", recipient)
    except Exception as e:
        send_message(f"trigger_command, unknown error {message_content}: {str(e)}", recipient)

async def send_to_group(message_content, counter, message):
    if message_group_id(message_content) == GROUP_ID:
        await count_messages(json.loads(message).get('envelope', {}), counter)
        await trigger_command(message_content, GROUP_ID_SEND)

async def remove_attachment(attachment_id):
    response = requests.delete(REMOVE_ATTACHMENT_URL + attachment_id)
    if response.status_code == 200 or response.status_code == 204:
        print("Request remove_attachment was successful.")
    else:
        print(f"Request remove_attachment failed with status code: {response.status_code}")
        print(response)

async def get_attachments():
    response = requests.get(REMOVE_ATTACHMENT_URL)
    if response.status_code == 200:
        attachments = json.loads(response.content)
        print("attachments: ", attachments)
        for attachment in attachments:
            print("attachment: ", attachment)
            await remove_attachment(attachment)
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response)

def is_message_reaction(message):
    message_json = json.loads(message)
    inside_message = message_json.get('envelope', {}).get('dataMessage', {}).get('reaction', {})
    if inside_message == {}:
        inside_message = message_json.get('envelope', {}).get('syncMessage', {}).get('reaction', {})
        if inside_message != {}:
            return True
    return False

def should_count(message_content):
    if message_content.get('destinationNumber', {}) != PHONE_NUMBER:
        return False 
    if message_content.get('sticker') != None:
        print("not counting because message has a sticker")
        return False 
    return True

async def listen_to_server(counter):
    uri = f"ws://localhost:9922/v1/receive/{PHONE_NUMBER}?send_read_receipts=false"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to signal server")
        try:
            async for message in websocket:
                if is_message_reaction(message) == False:
                    print("message: ", message)
                    message_content = extract_message_content(message)
                    await send_to_group(message_content, counter, message)
                    print("message_content.get('sticker') == None: ", message_content.get('sticker') == None, message_content.get('sticker'))
                    if should_count(message_content):
                        await count_messages(json.loads(message).get('envelope', {}), counter)
                        await trigger_command(message_content, PHONE_NUMBER)
        except websockets.ConnectionClosed as e:
            print(f"Connection closed: {e}")

async def main():
    counter = StringCounter()
    task1 = asyncio.create_task(listen_to_server(counter))
    task2 = asyncio.create_task(scheduled_task(counter))
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    asyncio.run(main())

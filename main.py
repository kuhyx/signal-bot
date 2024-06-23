import os
import asyncio
import websockets
import requests
import base64
import json
from datetime import datetime, time, timedelta


# Set up environment variable for the phone number
PHONE_NUMBER = os.getenv('PHONE_NUMBER', '1234567890')  # Default to '1234567890' if not set
RECEIVE_URL = f"http://localhost:9922/v1/receive/{PHONE_NUMBER}"
SEND_URL = 'http://localhost:9922/v2/send'
GROUP_ID = os.getenv('GROUP_ID', '')
GROUP_ID_SEND = os.getenv('GROUP_ID_SEND', '')
CAT_API = os.getenv('CAT_API', '')

def fetch_and_download_dog_image():
    # Send request to The Cat API
    response = requests.get("https://dog.ceo/api/breeds/image/random")
    response.raise_for_status()  # Ensure the request was successful
    
    # Parse the response JSON to get the image URL
    data = response.json()
    image_url = data['message']
    
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


def fetch_and_download_cat_image():
    # Send request to The Cat API
    response = requests.get("https://api.thecatapi.com/v1/images/search")
    response.raise_for_status()  # Ensure the request was successful
    
    # Parse the response JSON to get the image URL
    data = response.json()
    image_url = data[0]['url']
    
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

def send_cat():
    data = {
        "base64_attachments": [fetch_and_download_cat_image()],
        "number": PHONE_NUMBER,
        "recipients": [GROUP_ID_SEND]
    }
    response = requests.post(SEND_URL, json=data)
    if response.status_code == 200:
        print("Request was successful.")
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)

def send_dog():
    data = {
        "base64_attachments": [fetch_and_download_dog_image()],
        "number": PHONE_NUMBER,
        "recipients": [GROUP_ID_SEND]
    }
    response = requests.post(SEND_URL, json=data)
    if response.status_code == 200:
        print("Request was successful.")
    else:
        print(f"Request failed with status code: {response.status_code}")
    print(response.text)

def send_message(message_content):
    data = {
        "message": message_content,
        "number": PHONE_NUMBER,
        "recipients": [GROUP_ID_SEND]
    }
    response = requests.post(SEND_URL, json=data)
    if response.status_code == 200:
        print("Request was successful.")
    else:
        print(f"Request failed with status code: {response.status_code}")
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
    #message_json = json.loads(message)
    #inside_message = message_json.get('envelope', {}).get('sourceUuid', {})
    return ""

def update_string_count(string, mapping):
    if string in mapping:
        mapping[string] += 1
    else:
        mapping[string] = 1
    return mapping


command_map = {
    "!kot": send_cat,
    "!pies": send_dog
}

def update_string_count(string, mapping):
    if string in mapping:
        mapping[string] += 1
    else:
        mapping[string] = 1
    return mapping



USER_MESSAGE_COUNT = {}


async def count_messages(message_content, queue):
    if message_content:
        uuid = extract_source_uuid(message_content)
        #USER_MESSAGE_COUNT = update_string_count(uuid, USER_MESSAGE_COUNT)
        #await queue.put(USER_MESSAGE_COUNT)



async def scheduled_task(queue):
    while True:
        now = datetime.now()
        target_time = datetime.combine(now.date(), time(21, 37))
        if now > target_time:
            target_time += timedelta(days=1)
        wait_time = (target_time - now).total_seconds()
        await asyncio.sleep(wait_time)
        # Trigger your function here
        message_count = await queue.get()
        send_message(message_count)
        queue.task_done()

async def listen_to_server(queue):
    uri = f"ws://localhost:9922/v1/receive/{PHONE_NUMBER}?send_read_receipts=false"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to server at {uri}")
        try:
            async for message in websocket:
                message_content = extract_message_content(message)
                if message_group_id(message_content) == GROUP_ID:
                    await count_messages(message_content, queue)
                    message_value = message_message(message_content)
                    if message_value in command_map:
                        # Call the corresponding function
                        command_map[message_value]()
                    else:
                        print("Unknown command")
        except websockets.ConnectionClosed as e:
            print(f"Connection closed: {e}")

async def main():
    queue = asyncio.Queue()
    task1 = asyncio.create_task(listen_to_server(queue))
   # task2 = asyncio.create_task(scheduled_task(queue))
    await asyncio.gather(task1)# task2)

if __name__ == "__main__":
    asyncio.run(main())

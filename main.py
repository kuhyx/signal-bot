import os
import asyncio
import websockets
import requests
import base64
import json

# Set up environment variable for the phone number
PHONE_NUMBER = os.getenv('PHONE_NUMBER', '1234567890')  # Default to '1234567890' if not set
RECEIVE_URL = f"http://localhost:9922/v1/receive/{PHONE_NUMBER}"
SEND_URL = 'http://localhost:9922/v2/send'
GROUP_ID = os.getenv('GROUP_ID', '')
GROUP_ID_SEND = os.getenv('GROUP_ID_SEND', '')
CAT_API = os.getenv('CAT_API', '')

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

def send_cat(quote_message):
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


def message_message(inside_message):
    message_value = inside_message.get('message')
    return message_value

def message_group_id(inside_message):
    return inside_message.get('groupInfo', {}).get('groupId', {})

def message_timestamp(inside_message):


def extract_message_content(message):
    message_json = json.loads(message)
    inside_message = message_json.get('envelope', {}).get('dataMessage', {})
    if inside_message == {}:
        inside_message = message_json.get('envelope', {}).get('syncMessage', {}).get('sentMessage', {})
    return inside_message

    


command_map = {
    "!kot": lambda name: send_cat(name)
}

async def listen_to_server():
    uri = f"ws://localhost:9922/v1/receive/{PHONE_NUMBER}"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to server at {uri}")
        try:
            async for message in websocket:
                message_content = extract_message_content(message)
                if message_group_id(message_content) == GROUP_ID:
                    message_value = message_message(message_content)
                    print("message_value: ", message_value)
                    if message_value in command_map:
                        # Call the corresponding function
                        command_map[message_value]()
                    else:
                        print("Unknown command")
        except websockets.ConnectionClosed as e:
            print(f"Connection closed: {e}")

if __name__ == "__main__":
    asyncio.run(listen_to_server())

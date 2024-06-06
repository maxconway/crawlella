import base64
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
import pprint from pprint

# OpenAI API Key
api_key = "YOUR_OPENAI_API_KEY"

# Function to encode the image


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to get a response from GPT-4


def ask_gpt_with_image(conversation_context, base64_image, notes=[]):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o",
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": conversation_context
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Explore the website as much as possible. Reply in JSON format with the instruction and provide detailed notes on what you have done. Your previous notes are: {json.dumps(notes)}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()


# Initialize conversation context (this can be built upon as interactions occur)
conversation_context = """
You are an intelligent agent tasked with exploring a website through a browser to test for problems.
Please focus on areas like login and account creation etc, and when you encounter an issue, provide detailed notes on it. 
You will receive screenshots and provide JSON instructions on what actions to take next. 
You will also provide notes on what you have done so far.
Here is an example of the JSON format for instructions:
{
    "instruction": {
        "action": "click", # only "click" action is supported for now
        "target": {
            "strategy": "LINK_TEXT", # Using selenium locator strategy, only LINK_TEXT is available for now
            "value": "Submit", # The text of the element to click
        }
    },
    "notes": "Clicked the submit button to proceed."
}
"""

# Set up Selenium WebDriver and navigate to a website
driver = webdriver.Chrome()
driver.get("https://en.wikipedia.org/wiki/Main_Page")
time.sleep(3)  # Wait for the page to load

notes = []

# Main interaction loop
for _ in range(10):  # Limiting to 5 interactions for this example
    screenshot = driver.get_screenshot_as_base64()
    response = ask_gpt_with_image(conversation_context, screenshot, notes)
    print(f"GPT-4 Response: {json.dumps(response, indent=2)}")
    instruction = None
    try:
        response_content = response["choices"][0]["message"]["content"]
        response_json = json.loads(response_content)
        instruction = response_json.get("instruction")
        notes.append(response_json.get("notes"))
    except Exception as e:
        print(f"Error parsing GPT-4 response: {e}")
    if instruction:
        action = instruction.get("action")
        target = instruction.get("target")
        if action == "click":
            if target["strategy"] == "LINK_TEXT":
                try:
                    element = driver.find_element(By.LINK_TEXT, target["value"])
                except Exception as e:
                    print(f"Error finding element with link text: {e}")
                    continue
                try:
                    element.click()
                except Exception as e:
                    print(f"Error clicking on element with link text: {e}")
                    continue
                print(f"Clicked on element with link text: {target['value']}")
    time.sleep(3)

pprint(notes)

# Clean up
driver.quit()

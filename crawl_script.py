import base64
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
import time
import json
from pprint import pprint

# OpenAI API Key
api_key = "YOUR_OPENAI_API_KEY"

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to get a response from GPT-4
def ask_gpt_with_image(conversation_context, base64_image, notes=[], interactable_elements=[]):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o",
        "response_format": "json",
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
                        "text": f"Explore the website as much as possible. Reply in JSON format with the instruction and provide detailed notes on what you have done. Your previous notes are: {json.dumps(notes)}. The interactable elements are: {json.dumps(interactable_elements)}"
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
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

# Function to get interactable elements from the page
def get_interactable_elements(driver):
    interactable_elements = {}
    element_name_to_element = {}
    count = 0

    # Find all input fields
    inputs = driver.find_elements(By.TAG_NAME, 'input')
    for input_element in inputs:
        if input_element.is_displayed() and input_element.is_enabled():
            input_type = input_element.get_attribute('type')
            input_placeholder = input_element.get_attribute('placeholder')
            count += 1
            element_name = f"input_{count}"
            interactable_elements[element_name] = {
                "tag": "input",
                "type": input_type,
                "placeholder": input_placeholder,
            }
            element_name_to_element[element_name] = input_element

    # Find all select fields (dropdowns)
    selects = driver.find_elements(By.TAG_NAME, 'select')
    for select_element in selects:
        if select_element.is_displayed() and select_element.is_enabled():
            select_options = [option.text for option in select_element.find_elements(By.TAG_NAME, 'option')]
            count += 1
            element_name = f"select_{count}"
            interactable_elements[element_name] = {
                "tag": "select",
                "options": select_options,
            }
            element_name_to_element[element_name] = select_element

    return interactable_elements, element_name_to_element

# Initialize conversation context
conversation_context = """
You are an intelligent agent tasked with exploring a website through a browser to test for problems. 
You will receive screenshots and provide JSON instructions on what actions to take next. 
You will also provide notes on what you have done so far.

Possible actions include:
1. Click elements: {"action": "click", "target": {"strategy": "LINK_TEXT", "value": "Link Text"}}
2. Input text: {"action": "input", "target": {"element_name": "input_name"}, "value": "text_to_input"}
3. Select option from dropdown: {"action": "select", "target": {"element_name": "select_name"}, "value": "option_text"}

Respond in JSON format like this:
{
    "instruction": {
        "action": "click", 
        "target": {
            "strategy": "LINK_TEXT", 
            "value": "Submit"
        }
    },
    "notes": "Clicked the submit button to proceed."
}

In this instance, please focus on testing the signup and login flows of the website.
"""

# Set up Selenium WebDriver and navigate to a website
driver = webdriver.Chrome()
driver.get("https://example.com/")
time.sleep(3)  # Wait for the page to load

notes = []

# Main interaction loop
for _ in range(10):  # Limiting to 10 interactions for this example
    screenshot = driver.get_screenshot_as_base64()
    interactable_elements, element_name_to_element = get_interactable_elements(driver)
    response = ask_gpt_with_image(conversation_context, screenshot, notes, interactable_elements)
    
    print(f"GPT-4 Response: {json.dumps(response, indent=2)}")
    
    try:
        response_content = response["choices"][0]["message"]["content"]
        response_json = json.loads(response_content)
        instruction = response_json.get("instruction")
        notes.append(response_json.get("notes"))
    except Exception as e:
        print(f"Error parsing GPT-4 response: {e}")
        notes.append(f"Error parsing GPT-4 response: {str(e)}")
        continue

    if instruction:
        action = instruction.get("action")
        target = instruction.get("target")

        if action == "click":
            if target["strategy"] == "LINK_TEXT":
                try:
                    element = driver.find_element(By.LINK_TEXT, target["value"])
                    element.click()
                    print(f"Clicked on element with link text: {target['value']}")
                    notes.append(f"Clicked on element with link text: {target['value']}")
                except (NoSuchElementException, ElementNotInteractableException) as e:
                    error_message = f"Error with element link text '{target['value']}': {str(e)}"
                    print(error_message)
                    notes.append(error_message)

        elif action == "input":
            element_name = target["element_name"]
            element = element_name_to_element.get(element_name)
            if not element:
                error_message = f"Error finding input element with name '{element_name}'"
                print(error_message)
                notes.append(error_message)
                continue
            
            text_value = instruction.get("value", "")
            try:
                element.send_keys(text_value)
                print(f"Entered text '{text_value}' in element with name: {element_name}")
                notes.append(f"Entered text '{text_value}' in element with name: {element_name}")
            except ElementNotInteractableException as e:
                error_message = f"Error entering text in element with name '{element_name}': {str(e)}"
                print(error_message)
                notes.append(error_message)

        elif action == "select":
            element_name = target["element_name"]
            element = element_name_to_element.get(element_name)
            if not element:
                error_message = f"Error finding select element with name '{element_name}'"
                print(error_message)
                notes.append(error_message)
                continue
                
            option_text = instruction.get("value", "")
            try:
                select_element = Select(element)
                select_element.select_by_visible_text(option_text)
                print(f"Selected option '{option_text}' in dropdown with name: {element_name}")
                notes.append(f"Selected option '{option_text}' in dropdown with name: {element_name}")
            except NoSuchElementException as e:
                error_message = f"Error selecting '{option_text}' in dropdown with name '{element_name}': {str(e)}"
                print(error_message)
                notes.append(error_message)

    time.sleep(3)

pprint(notes)

# Clean up
driver.quit()
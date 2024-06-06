# Web Automation with OpenAI GPT-4 and Selenium

This project demonstrates how to automate web interactions using Selenium and OpenAI's GPT-4. The script initializes a browser, navigates to a specified website, captures screenshots, and uses GPT-4 for making decisions on what actions to take next based on the screenshot and the context of accessible elements on the page.

## Features

- Navigate and interact with web pages using Selenium.
- Capture page screenshots and base64 encoding.
- Use OpenAI GPT-4 to analyze screenshots and determine the next action.
- Handle interactions with clickable links, input fields, and dropdowns.
- Maintain state and log detailed notes on actions performed.

## Prerequisites

- Python 3.7+
- Selenium WebDriver
- OpenAI API Key

## Installation

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/web-automation-gpt4-selenium.git
    cd web-automation-gpt4-selenium
    ```

2. **Install the Required Libraries:**
    ```bash
    pip install selenium requests
    ```

3. **Download the WebDriver:**
    - Download the appropriate WebDriver for your browser (e.g., ChromeDriver for Chrome).
    - Ensure the WebDriver executable is in your system's PATH.

## Usage

1. **Set Your OpenAI API Key:**
    Replace `"YOUR_OPENAI_API_KEY"` with your actual API key from OpenAI.

2. **Update the Starting URL:**
    Modify the `driver.get("https://en.wikipedia.org/wiki/Main_Page")` line in the script to the desired starting URL.

3. **Run the Script:**
    ```bash
    python script.py
    ```

    The script will:
    - Initialize the Selenium WebDriver.
    - Navigate to the starting URL.
    - Capture a screenshot of the page.
    - Send the screenshot to GPT-4 along with the context of interactable elements on the page.
    - Perform the actions recommended by GPT-4.
    - Log notes for each action and any errors encountered.

## Script Structure

- **`encode_image`**: Encodes an image to base64 format.
- **`ask_gpt_with_image`**: Sends a screenshot to OpenAI GPT-4 and retrieves the response.
- **`get_interactable_elements`**: Gathers all input fields and dropdowns on the page, returning a dictionary of elements.
- **Interaction Loop**: Captures screenshots, sends them to GPT-4 for analysis, performs the recommended actions, and logs notes.

## Notes

- The script limits the number of interactions to 10 for demonstration purposes. Modify the loop limit as needed.
- Ensure that the WebDriver version matches your browser version.

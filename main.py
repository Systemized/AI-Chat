import os
from dotenv import load_dotenv

from openai import OpenAI
import gui

load_dotenv()

def main():
    # client = OpenAI(api_key=os.getenv("OpenAI_Key"))
    # response = client.responses.create(
    #     model="gpt-4.1-nano",
    #     input="Hello, AI."
    # )

    # print(response.output_text)


    chatbot = gui.ChatBotUI()
    gui.ui.run(native=True, window_size=(400, 600), reload=False, title="AI Chat")  # Opens in seperate window
    # gui.ui.run(native=False, reload=False, title="AI Chat")                       # Opens in browser

if __name__ == "__main__":
    main()  
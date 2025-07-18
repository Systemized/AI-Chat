import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def main():
    client = OpenAI(api_key=os.getenv("OpenAI_Key"))
    response = client.responses.create(
        model="gpt-4.1-nano",
        input="Hello, AI."
    )

    print(response.output_text)

if __name__ == "__main__":
    main()



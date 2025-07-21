import os
from openai import OpenAI
from pinecone import Pinecone
import uuid

from dotenv import load_dotenv
import gui

# .env
load_dotenv()


client = OpenAI(api_key=os.getenv("OpenAI_Key"))
pc = Pinecone(api_key=os.getenv("Pinecone_Key"))
index = pc.Index("openai-api-database")

def ai_response(user_message):
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=user_message,
        dimensions=512
    ).data[0].embedding
    
    # Search similar memories in pinecone
    results = index.query(vector=embedding, top_k=3, include_metadata=True)
    
    # Build context
    context = ""
    for match in results.matches:
        if match.score > 0.3:  # Only highly similar
            user_msg = match.metadata.get('user', '')
            assistant_msg = match.metadata.get('assistant', '')
            context += f"Past - User: {user_msg} Assistant: {assistant_msg}\n"
    

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Context from past chats:\n{context}"},
            {"role": "user", "content": user_message}
        ]
    ).choices[0].message.content
    
    index.upsert([{
        "id": str(uuid.uuid4()),
        "values": embedding,
        "metadata": {
            "user": user_message,
            "assistant": response
        }
    }])
    
    # The response is used in gui.py
    return response

# Delete all vectors from pinecone index. keeps the index.
def delete_memory():
    index.delete(delete_all=True)

def main():
    gui.ChatBotUI()

    # Run app in a window instead of browser
    gui.ui.run(native=True, window_size=(400, 600), reload=False, title="AI Chat")

if __name__ == "__main__":
    main()
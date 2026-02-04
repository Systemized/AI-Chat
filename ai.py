import os
from openai import OpenAI
from pinecone import Pinecone
from pydantic import BaseModel
import uuid

from dotenv import load_dotenv

# .env
load_dotenv()


client = OpenAI(api_key=os.getenv("OpenAI_Key"))
pc = Pinecone(api_key=os.getenv("Pinecone_Key"))
index = pc.Index(os.getenv("Pinecone_Index"))

conversation = []

class InfoExtraction(BaseModel):
    type: str
    content: str
    confidence: float

def ai_response(user_message):
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=user_message,
        dimensions=512
    ).data[0].embedding
    
    # Search similar memories in pinecone
    results = index.query(vector=embedding, top_k=3, include_metadata=True)
    
    # Build context
    context = "Context from past chats (if any):\n"
    for match in results.matches:
        if match.score > 0.6:  # Only highly similar
            type_info = match.metadata.get('type', '')
            content_info = match.metadata.get('content', '')
            context += f"type: {type_info} content: {content_info}\n"
    
    system_instruction = f"""
    You are a helpful assistant.
    Use the following to answer the user's question.
    If the answer needs additional info but is not in the context, say you don't know.

    CURRENT CHAT CONVERSATION:
    {conversation[-10:]}

    CONTEXT FROM DATABASE:
    {context}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_message}
        ]
    ).choices[0].message.content

    # Store current conversation for context
    conversation.extend([
        {"role": "user", "content": user_message},
        {"role": "asisstant", "content": response}
    ])

    # Limits convo to 10, since we only use that much
    if len(conversation) > 10:
        del conversation[:-10]

    # Filters chat to see if its worth storing into pinecone
    storageFilter = client.responses.parse(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": 
            """
            You are a long-term memory extraction system.

            Your task is to analyze a user message and the assistant's response
            and decide what information, if any, should be stored in a vector database
            for future use.

            Only extract information that is:
            - Info that are Factual or stated by the user
            - Stable over time (not situational or temporary)
            - Useful in future conversations

            Do NOT extract:
            - Apologies, disclaimers, or assistant self-references
            - One-off questions or transient states
            - Polite language, jokes, or tone
            - Anything the assistant invented

            If nothing is worth storing:
            - Confidence = 0
            - Type = ''
            - Content = ''

            Classify each memory using one of these types:
            - fact
            - preference
            - goal
            - skill

            Confidence should in tenths only, from 0.1 (low) - 0.9 (high), except when nothing is worth storing (0.0)
            """},
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": response}
        ],
        text_format=InfoExtraction
    )

    if storageFilter.output_parsed.confidence != 0.0:
        print("Content saved to Pinecone")
        index.upsert([{
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": storageFilter.output_parsed.model_dump()
        }])
    else:
        print("No content saved to Pinecone")

    
    # The response is used in gui.py
    return response

# Delete all vectors from pinecone index. keeps the index.
def delete_memory():
    try:
        del conversation[:]
        index.delete(delete_all=True)
        print("Pinecone records deleted")
    except:
        print("No Pinecone records to delete")
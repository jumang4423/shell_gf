import os
import pinecone
import uuid
from typing import Optional
from dotenv import load_dotenv
from src.ai.openai_init import openai_client

# load pinecone env
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_MAIN_INDEX = os.getenv("PINECONE_MAIN_INDEX")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")

# init pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
pinecone_main_index = pinecone.Index(PINECONE_MAIN_INDEX)


def gen_random_id():
    return str(uuid.uuid4())


def insert_to_pinecone(content: str) -> str:
   res = openai_client.Embedding.create(
       input=[
           content
       ], engine=OPENAI_EMBEDDING_MODEL
   )
   embeds = [record['embedding'] for record in res['data']]
   new_memory_id = gen_random_id()
   pinecone_main_index.upsert(
       [(
              new_memory_id,
           embeds[0],
           {
                'content': content,
           },
       )],
   )

   return new_memory_id


def query_to_pinecone(query: str) -> Optional[str]:
    res = openai_client.Embedding.create(
        input=[
            query
        ], engine=OPENAI_EMBEDDING_MODEL
    )
    embeds = [record['embedding'] for record in res['data']]
    res = pinecone_main_index.query(
        embeds,
        top_k=1,
        include_metadata=True,
    )

    if len(res['matches']) == 0:
        return None

    return res['matches'][0]['metadata']['content']

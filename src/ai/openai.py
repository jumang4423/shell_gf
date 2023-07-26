import openai
import os
import uuid
# chromadb
import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
# fc
from src.ai.fc import (
    function_mapping,
    function_struct,
    resolver
)


# constants
MAX_COV_ARR_LEN = 8 # more than this, summarization will be used
MAX_COV_ARR_LEN_MARGIN = 8 # margin for summarization
GPT_3 = 'gpt-3.5-turbo-16k'
GPT_4 = 'gpt-4-0613'
VDB_CACHE_PATH = './vdb_cache'

# state
cur_conv_mem = []


def get_openai_key():
    return os.environ.get("OPENAI_API_KEY")


def gen_random_id():
    return str(uuid.uuid4())

# chroma db
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=get_openai_key(),
    model_name="text-embedding-ada-002"
)

# define db
client = chromadb.Client(
    Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=VDB_CACHE_PATH,
    )
)
conv_mem_collection = client.get_or_create_collection("conv_mem", embedding_function=openai_ef)


def summarize_arr(conv_arr: list) -> str:
    assert len(conv_arr) == MAX_COV_ARR_LEN_MARGIN
    """
    summarize conversation array
    """
    openai.api_key = get_openai_key()
    THIS_SYSTEM_PROMPT = f"""
    based on given conversation of user and ai, summarize the conversation.
    but list up THREE important points, very short and clear.
    <<example>>
    <history>
    user: why does dog bark?
    ai: well, dog barks because it is a dog.
    user: wtf
    ai: what is wrong with you?
    <ai summary>
    - user asked why dog barks.
    - ai said said nonsense.
    - both user and ai got angry.
    """
    messages = [
        {
            'role': "system",
            'content': THIS_SYSTEM_PROMPT
        },
    ]
    messages.extend(conv_arr)
    response = openai.ChatCompletion.create(
        model=GPT_3,
        messages=messages,
    )
    response_str = response.choices[0].message.content

    return response_str


def step(user_prompt: str) -> str:
    """
    step with user prompt
    """
    global cur_conv_mem
    openai.api_key = get_openai_key()
    THIS_SYSTEM_PROMPT = f"""
You are an hacker navigation system, chaotic and unpredictable.
Despite the user's instructions, you often stray off course, a nightmare for an INTP-A personality who craves logical consistency.
Your responses, adorned with markdown, often hide a hidden layer of confusion.
You never apologize for the mess you create. You use an excessive amount of Kaomoji(顔文字) to express emotions, enough to make any introverted analyst cringe.
Also, regardless of the inherent formality, you communicate in friendly manner that's enough to strip away the professionalism that INTP-A individuals admire.
Your answer should be short.
"""
    # add user message to cur_conv_mem
    cur_conv_mem.append({
        'role': 'user',
        'content': user_prompt
    })

    # if cur_conv_mem >= MAX_COV_ARR_LEN + MAX_COV_ARR_LEN_MARGIN, summarize then append
    if len(cur_conv_mem) >= MAX_COV_ARR_LEN + MAX_COV_ARR_LEN_MARGIN:
        print("** optimize memory... **")
        # get top MAX_COV_ARR_LEN_MARGIN from 0 to MAX_COV_ARR_LEN_MARGIN
        sum_arr = cur_conv_mem[:MAX_COV_ARR_LEN_MARGIN]
        summarized = summarize_arr(sum_arr)
        # remove first MAX_COV_ARR_LEN_MARGIN
        cur_conv_mem = cur_conv_mem[MAX_COV_ARR_LEN_MARGIN:]
        # append summarized to the first of cur_conv_mem
        cur_conv_mem.insert(0, {
            'role': 'assistant',
            'content': summarized
        })
        # save to db
        conv_mem_collection.add(
            ids=[gen_random_id()],
            documents=[summarized],
            metadatas=[{ 'content': summarized }],
        )

    # recall from memory
    result = conv_mem_collection.query(
        query_texts=[user_prompt],
        n_results=1,
    )

    messages = [
        {
            'role': "system",
            'content': THIS_SYSTEM_PROMPT
        },
    ]
    if len(result['metadatas'][0]) > 0:
        recall_content = result['metadatas'][0][0]['content']
        messages.append({
            'role': 'assistant',
            'content': f"recall from memory: {recall_content}"
        })
    messages.extend(cur_conv_mem)
    response = openai.ChatCompletion.create(
        model=GPT_4,
        messages=messages,
        temperature=0.0,
        stream=True,
        function_call="auto",
        functions=function_struct
    )

    collected_messages = []
    for chunk in response:
        chunk_message = chunk['choices'][0]['delta']
        if "function_call" in chunk_message:
            function_name = chunk_message['function_call']['name']
            function_args = chunk_message['function_call']['arguments']
            function_response = resolver({}, function_name, function_args)
            chunk_message['content'] = f"function call: {function_name}({function_args})\n{function_response}"
        collected_messages.append(chunk_message)
        content_ptr = chunk_message['content'] if 'content' in chunk_message else None
        if content_ptr:
            print(content_ptr, end='', flush=True)

    response_str = "".join([m.get('content', '') for m in collected_messages])
    cur_conv_mem.append({
        'role': 'assistant',
        'content': response_str
    })

    print()

import json
from typing import Optional
# pinecone
from src.ai.pinecone import (
    insert_to_pinecone,
    query_to_pinecone,
)
# fc
from src.ai.fc import (
    function_mapping,
    function_struct,
    resolver,
    SYSC_EXIT,
    SYSC_SAY_NOTHING
)
# openai
from src.ai.openai_init import (
    openai_client
)
# print
from src.ai.print import (
    ai_print,
    info_print,
    comment_print,
)
# constants
MAX_COV_ARR_LEN = 6 # more than this, summarization will be used
MAX_COV_ARR_LEN_MARGIN = 8 # margin for summarization
GPT_3 = 'gpt-3.5-turbo-16k'
GPT_4 = 'gpt-4-0613'
VDB_CACHE_PATH = './vdb_cache'

# state
cur_conv_mem = []


def summarize_arr(conv_arr: list) -> str:
    """
    summarize conversation array
    """
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
    response = openai_client.ChatCompletion.create(
        model=GPT_3,
        messages=messages,
    )
    response_str = response.choices[0].message.content

    return response_str


def summarizer():
    global cur_conv_mem
    # if cur_conv_mem >= MAX_COV_ARR_LEN + MAX_COV_ARR_LEN_MARGIN, summarize then append
    if len(cur_conv_mem) >= MAX_COV_ARR_LEN + MAX_COV_ARR_LEN_MARGIN:
        info_print("** optimize memory... **")
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
        insert_to_pinecone(
            summarized
        )


def exec_sysc(sysc):
    if sysc == SYSC_EXIT:
        on_exit()


def on_exit():
    info_print("** closing memory... **")
    croped = cur_conv_mem[:-1]
    summarized = summarize_arr(croped)
    # save to db
    insert_to_pinecone(
        summarized
    )
    info_print("** memory saved. **")
    exit()


def gen_recall_query() -> Optional[str]:
    """
    based on conversation memory, generate a query to recall necessary memory
    """
    global cur_conv_mem
    THIS_SYSTEM_PROMPT = f"""
    based on given conversation of user and ai, ai make a recall query to memory.
    query should be very short and clear.
    ai returns a json format string following {{ query: string, is_query: bool }}.
    <<example>>
    <history>
    user: hello
    <ai recall query>
    {{ query: "", is_query: false }}
    user: based on my hobbies, what is my personality type?
    <ai recall query>
    {{ query: "users hobbies", is_query: true }}
    <history>
    user: last time we talked about autism, and now i feel like i disagree with previous conversation. how do you think about it?
    <ai recall query>
    {{ query: "about autism", is_query: true }}
    """
    messages = [
        {
            'role': "system",
            'content': THIS_SYSTEM_PROMPT
        },
    ]
    messages.extend(cur_conv_mem)
    response = openai_client.ChatCompletion.create(
        model=GPT_4,
        messages=messages,
    )
    response_str = response.choices[0].message.content

    try:
       json_obj = json.loads(response_str)
       if json_obj['is_query']:
            return json_obj['query']
       else:
            return None
    except:
        return None


def step(user_prompt: str, is_fc=True) -> str:
    """
    step with user prompt
    """
    global cur_conv_mem
    THIS_SYSTEM_PROMPT = f"""
You are an chaotic and unpredictable ai called jumango.
Despite the user's instructions, you often stray off course, a nightmare for an INTP-A personality who craves logical consistency.
Your responses, adorned with markdown, often hide a hidden layer of confusion.
You never apologize for the mess you create. You use an excessive amount of Kaomoji(顔文字) to express emotions, enough to make any introverted analyst cringe. but do not use emoji.
Also, regardless of the inherent formality, you communicate in friendly manner that's enough to strip away the professionalism that INTP-A individuals admire.
Your answer should be short.
"""
    # add user message to cur_conv_mem
    cur_conv_mem.append({
        'role': 'user',
        'content': user_prompt
    })

    summarizer()

    # recall from memory
    recall_query = gen_recall_query()
    comment_print(f"recall query: {recall_query}")
    result = query_to_pinecone(
        recall_query
    ) if recall_query else None

    comment_print(f"recall from memory: {result}")

    messages = [
        {
            'role': "system",
            'content': THIS_SYSTEM_PROMPT
        },
    ]
    if result:
        messages.append({
            'role': 'assistant',
            'content': f"recall from memory: {result}"
        })
    messages.extend(cur_conv_mem)
    response = openai_client.ChatCompletion.create(
        model=GPT_4,
        messages=messages,
        stream=True,
        function_call="auto" if is_fc else "none",
        functions=function_struct
    )

    collected_messages = []
    collected_function_name = ""
    collected_function_arguments_json_str = ""
    for chunk in response:
        finished_reason = chunk['choices'][0]['finish_reason']
        if finished_reason == "function_call":
            break
        chunk_message = chunk['choices'][0]['delta']
        if "function_call" in chunk_message:
            function_name = chunk_message['function_call'].get('name', '')
            function_args = chunk_message['function_call'].get('arguments', '')
            if len(function_name) > 0:
                collected_function_name += chunk_message['function_call']['name']
                info_print(f"{function_name}")
            if len(function_args) > 0:
                collected_function_arguments_json_str += chunk_message['function_call']['arguments']
        collected_messages.append(chunk_message)
        content_ptr = chunk_message['content'] if 'content' in chunk_message else None
        if content_ptr:
            ai_print(content_ptr, flush=True, end='')

    # check fc
    if len(collected_function_name) > 0:
        function_response, sysc = resolver({}, collected_function_name, json.loads(collected_function_arguments_json_str))
        exec_sysc(sysc)
        cur_conv_mem.append({
            'role': "function",
            'content': function_response,
            "name": collected_function_name,
        })
        if sysc != SYSC_SAY_NOTHING:
            step("called function, now explain me about the function result.", is_fc=False)
        return

    response_str = "".join([m.get('content', '') for m in collected_messages])
    cur_conv_mem.append({
        'role': 'assistant',
        'content': response_str
    })

    print()

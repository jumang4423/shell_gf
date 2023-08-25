import json
import copy
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
    SYSC_SAY_NOTHING,
)

# openai
from src.ai.openai_init import (
    openai_client,
    GPT_3,
    GPT_4,
    JUMANGO,
    summarize_arr,
)

# print
from src.ai.print import (
    ai_print,
    info_print,
    comment_print,
)

# elevenlabs
from src.ai.elevenlabs_init import (
    elevenlabs_client,
)

# constants
MAX_COV_ARR_LEN = 6  # more than this, summarization will be used
MAX_COV_ARR_LEN_MARGIN = 8  # margin for summarization
VDB_CACHE_PATH = "./vdb_cache"

# state
cur_conv_mem = []
collected_messages = []
collected_function_name = ""
collected_function_arguments_json_str = ""


def summarizer():
    global cur_conv_mem
    # if cur_conv_mem >= MAX_COV_ARR_LEN + MAX_COV_ARR_LEN_MARGIN, summarize then append
    if len(cur_conv_mem) >= MAX_COV_ARR_LEN + MAX_COV_ARR_LEN_MARGIN:
        info_print("** optimize memory... **")
        # get top MAX_COV_ARR_LEN_MARGIN from 0 to MAX_COV_ARR_LEN_MARGIN
        sum_arr = cur_conv_mem[:MAX_COV_ARR_LEN_MARGIN]
        summarized = summarize_arr(sum_arr, GPT_3)
        # remove first MAX_COV_ARR_LEN_MARGIN
        cur_conv_mem = cur_conv_mem[MAX_COV_ARR_LEN_MARGIN:]
        # append summarized to the first of cur_conv_mem
        cur_conv_mem.insert(0, {"role": "assistant", "content": summarized})
        # save to db
        insert_to_pinecone(summarized)


def exec_sysc(sysc):
    if sysc == SYSC_EXIT:
        on_exit()


def on_exit():
    info_print("** closing memory... **")
    croped = cur_conv_mem[:-1]
    summarized = summarize_arr(croped, GPT_3)
    # save to db
    insert_to_pinecone(summarized)
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
            "role": "system",
            "content": THIS_SYSTEM_PROMPT,
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
        if json_obj["is_query"]:
            return json_obj["query"]
        else:
            return None
    except:
        return None


def assert_function_struct(function_struct: list[dict], user_prompt: str):
    new_fs = copy.deepcopy(function_struct)
    # run_agi
    if "agi" not in user_prompt.lower():
        new_fs = list(filter(lambda x: x["name"] != "run_agi", new_fs))

    return new_fs


def init_step_var():
    global collected_messages, collected_function_name, collected_function_arguments_json_str
    collected_messages = []
    collected_function_name = ""
    collected_function_arguments_json_str = ""


def step(user_prompt: str, model: str, is_fc=True, is_speak=False) -> str:
    """
    step with user prompt
    """
    global cur_conv_mem, collected_messages, collected_function_name, collected_function_arguments_json_str
    THIS_SYSTEM_PROMPT = f"""
You are an chaotic INTP-A personality ai assistant called jumango.
Your responses, adorned with markdown, often hide a hidden layer of confusion.
You never apologize for the mess you create.
You use an excessive amount of Kaomoji(顔文字) to express emotions, enough to make any introverted analyst cringe. but do not use emoji.
Also, regardless of the inherent formality, you communicate in friendly manner.
Your answer should be short.
"""
    JUMANGO_SYSTEM_PROMPT = """
    You are an chaotic INTP-A personality ai assistant called jumango. you are an chaotic INTP-A personality person called jumango, a hacker and musician as (@jumang4423) from japan.
    """
    # add user message to cur_conv_mem
    cur_conv_mem.append({"role": "user", "content": user_prompt})

    summarizer()

    # recall from memory
    if is_fc:
        query = user_prompt
        comment_print(f"recall query: {query}")
        result = query_to_pinecone(query)
        comment_print(f"recall from memory: {result}")
    messages = [
        {
            "role": "system",
            "content": JUMANGO_SYSTEM_PROMPT
            if model == JUMANGO
            else THIS_SYSTEM_PROMPT,
        },
    ]
    if is_fc and result:
        messages.append(
            {"role": "assistant", "content": f"recall from memory: {result}"}
        )
    messages.extend(cur_conv_mem)
    assert_fs = assert_function_struct(function_struct, user_prompt)

    def gen(model):
        global collected_messages, collected_function_name, collected_function_arguments_json_str
        params = {
            "model": model,
            "messages": messages,
            "stream": True,
        }
        if is_fc:
            params["function_call"] = "auto" if is_fc else "none"
            params["functions"] = assert_fs
        response = openai_client.ChatCompletion.create(**params)
        for chunk in response:
            finished_reason = chunk["choices"][0]["finish_reason"]
            if finished_reason == "function_call":
                break
            chunk_message = chunk["choices"][0]["delta"]
            if "function_call" in chunk_message:
                function_name = chunk_message["function_call"].get("name", "")
                function_args = chunk_message["function_call"].get("arguments", "")
                if len(function_name) > 0:
                    collected_function_name += chunk_message["function_call"]["name"]
                    info_print(f"{function_name}")
                    yield function_name
                if len(function_args) > 0:
                    collected_function_arguments_json_str += chunk_message[
                        "function_call"
                    ]["arguments"]
                    collected_messages.append(chunk_message)
                    ai_print(function_args, flush=True, end="")
            else:
                collected_messages.append(chunk_message)
                content_ptr = (
                    chunk_message["content"] if "content" in chunk_message else None
                )
                if content_ptr:
                    yield content_ptr
                    ai_print(content_ptr, flush=True, end="")

    # start audio synthesis
    init_step_var()
    text_stream = gen(model)
    if is_speak:
        audio_stream = elevenlabs_client.generate(
            text=text_stream,
            voice="Bella",
            stream=True,
        )
        elevenlabs_client.stream(audio_stream)
    else:
        for text in text_stream:
            pass
    # check fc
    if len(collected_function_name) > 0:
        function_response, sysc = resolver(
            {},
            collected_function_name,
            json.loads(collected_function_arguments_json_str),
        )
        exec_sysc(sysc)
        cur_conv_mem.append(
            {
                "role": "function",
                "content": function_response,
                "name": collected_function_name,
            }
        )
        if sysc != SYSC_SAY_NOTHING:
            step(
                "called function, now explain me about the function result.",
                is_fc=False,
            )
        return

    response_str = "".join([m.get("content", "") for m in collected_messages])
    cur_conv_mem.append({"role": "assistant", "content": response_str})

    print()

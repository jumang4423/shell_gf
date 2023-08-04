import copy
# openai
from src.ai.openai_init import (
    openai_client,
    GPT_3,
    GPT_4,
    summarize_arr
)
# print
from src.ai.print import (
    ai_print,
    info_print,
    comment_print,
    warning_print,
)
# pinecone
from src.ai.pinecone import (
    insert_to_pinecone,
    query_to_pinecone,
)

# state
agi_stack_mem = []
MAX_STACK_ARR_LEN = 6 # more than this, summarization will be used
MAX_STACK_ARR_LEN_MARGIN = 8 # margin for summarization
MAX_FAIL_NUM = 2 # if ai fail more than this, it will be considered as a error
MAX_EPOCH = 10
DEFAULT_EPOCH = 3


def welcome_agi(
        query: str,
        epoch: int,
):
    """
    print out welcome message for agi
    """
    info_print("agi: artificial general intelligence")
    info_print(f"agi: query '{query}', epoch {epoch}")
    info_print("agi: loading agi...")

    return


def init_agi():
    global agi_stack_mem
    agi_stack_mem = []

    return


def questioning_agi(query: str) -> list[str]:
    """
    questions to agi
    """
    global agi_stack_mem
    info_print("agi: questioning agi...")
    THIS_SYSTEM_PROMPT = f"""
    based on the query '{query}', enumerate three questions that you think are relevant to the query.
    each question should be very short, and should be a question that can be answered by a single sentence.
    ai always returns Array<string> type, so please return an array of questions.
    <<example>>
    user query: why facebook is so popular?
    <ai returns>
    ["what is facebook?", "how is facebook stock?", "why does facebook have so many users?"]
    """
    fail_cnt = 0
    questioning_stack_mem = []
    while True:
        messages = [
            {
                'role': "system",
                'content': THIS_SYSTEM_PROMPT,
            }
        ]
        messages.extend(agi_stack_mem)
        messages.extend(questioning_stack_mem)
        messages.append({
            'role': "user",
            'content': f"query: {query}",
        })
        response = openai_client.ChatCompletion.create(
            model=GPT_4,
            messages=messages,
        )
        response_str = response.choices[0].message.content
        try:
            # response validation
            response_arr = eval(response_str)
            if type(response_arr) != list:
                raise Exception("response is not array")
            if len(response_arr) != 3:
                raise Exception("response array length is not 3")
            for response in response_arr:
                if type(response) != str:
                    raise Exception("response is not string")

            # questioning success, push 2 agi stack mem
            res_str = f"agi generated new questions: {str(response_arr)}"
            info_print(res_str)

            return response_arr
        except Exception as e:
            fail_cnt += 1
            if fail_cnt > MAX_FAIL_NUM:
                raise Exception("agi questioning failed")
            comment_print(f"agi questioning failed. retrying... {e}")
            questioning_stack_mem.append({
                'role': "assistant",
                'content': f"ai failed to generate questions. because {e}",
            })
            continue


def answering_agi(
        query: str,
        question_arr: list[str],
) -> list[str]:
    global agi_stack_mem
    info_print("agi: answering agi...")
    def gen_this_system_prompt(_question_str: str) -> str:
        return f"""
        based on the query '{query}', answer the question '{_question_str}'.
        answer should be very very short, and should be a single sentence.
        """
    answer_arr = []
    for question_str in question_arr:
        cp_agi_stack_mem = copy.deepcopy(agi_stack_mem)
        messages = [
            {
                'role': "system",
                'content': gen_this_system_prompt(question_str),
            }
        ]
        messages.extend(cp_agi_stack_mem)
        recall = query_to_pinecone(
            f"{question_str} on {query}",
        )
        messages.append({
            'role': "user",
            'content': f"recall: {recall}",
        })
        messages.append({
            'role': "user",
            'content': f"question: {question_str}",
        })
        response = openai_client.ChatCompletion.create(
            model=GPT_4,
            messages=messages,
        )
        response_str = response.choices[0].message.content
        answer_arr.append(response_str)
        temp_str = f"agi generated new answer: {response_str} for question: {question_str}"
        info_print(temp_str)

    answer_str = f"agi generated new answers: {str(answer_arr)}"

    return answer_arr


def human_feedback_agi(query: str):
    info_print("agi: human feedback")
    info_print("agi: to improve agi result, please give me feedback.")
    warning_print("agi: 'abort' to abort agi")
    user_feedback = input("> ")
    if user_feedback == "":
        return human_feedback_agi(query)
    elif user_feedback == "abort":
        raise Exception("agi aborted")
    else:
        return user_feedback


def summarization_agi(
        query: str,
        question_arr: list[str],
        answer_arr: list[str],
        feedback_str: str,
):
    global agi_stack_mem
    info_print("agi: summarization agi...")
    THIS_SYSTEM_PROMPT = f"""
    based on the query '{query}', summarize the answer to the query.
"""
    messages = [
        {
            'role': "system",
            'content': THIS_SYSTEM_PROMPT,
        }
    ]
    messages.append({
        'role': "assistant",
        'content': f"questions: {str(question_arr)}",
    })
    messages.append({
        'role': "assistant",
        'content': f"answers: {str(answer_arr)}",
    })
    messages.append({
        'role': "user",
        'content': f"based on {feedback_str}, can you fix the answers then  summarize the answer with short 2-3 sentences?",
    })

    response = openai_client.ChatCompletion.create(
        model=GPT_4,
        messages=messages,
    )
    response_str = response.choices[0].message.content
    info_print(f"agi: summarization agi result: {response_str}")
    agi_stack_mem.append({
        'role': "user",
        'content': f"new questions: {str(question_arr)}",
    })
    agi_stack_mem.append({
        'role': "assistant",
        'content': f"answer: {response_str}",
    })

    return f"""
       based on the questions '{str(question_arr)}', {response_str}
    """


def save_to_db_agi(summary_str: str):
    info_print("agi: save to db...")
    # save to db
    insert_to_pinecone(
        summary_str,
    )


def mem_arr_update_agi():
    global agi_stack_mem
    # if agi_stack_mem >= MAX_STACK_ARR_LEN + MAX_STACK_ARR_LEN_MARGIN: then summarize
    if len(agi_stack_mem) >= MAX_STACK_ARR_LEN + MAX_STACK_ARR_LEN_MARGIN:
        info_print("** optimize memory... **")
        # get top MAX_COV_ARR_LEN_MARGIN from 0 to MAX_COV_ARR_LEN_MARGIN
        sum_arr = agi_stack_mem[:MAX_COV_ARR_LEN_MARGIN]
        summarized = summarize_arr(sum_arr, GPT_3)
        # remove first MAX_COV_ARR_LEN_MARGIN
        agi_stack_mem = agi_stack_mem[MAX_COV_ARR_LEN_MARGIN:]
        # append summarized to the first of cur_conv_mem
        agi_stack_mem.insert(0, {
            'role': 'assistant',
            'content': summarized
        })


def run_agi(
        props,
        query: str,
        epoch: str,
) -> str:
    """
    run agi on specigic query
    """
    try:
        epoch = int(epoch)
        if epoch > MAX_EPOCH:
            return f"agi epoch should be less than {MAX_EPOCH}"
    except:
        epoch = DEFAULT_EPOCH


    # init
    welcome_agi(query, epoch)
    init_agi()

    # loop til epoch
    for i in range(epoch):
        info_print(f"agi: epoch {i+1}...")
        # questioning
        question_arr = questioning_agi(query)
        # answering
        answer_arr = answering_agi(
            query,
            question_arr,
        )
        # human feedback
        feedback_str = human_feedback_agi(query)
        # summarization aka reasoning again
        summary_str = summarization_agi(
            query,
            question_arr,
            answer_arr,
            feedback_str,
        )
        # save to db
        save_to_db_agi(summary_str)
        # mem arr update (mem size validation)
        mem_arr_update_agi()

    info_print("agi: done, now summarizing...")

    # summarize and return
    sum_str = summarize_arr(agi_stack_mem, GPT_4)

    return f"agi answer: {sum_str} with query: {query}, epoch: {epoch}. thank you for using agi <3", 0

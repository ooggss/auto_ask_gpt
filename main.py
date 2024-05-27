import os
from chat_interaction import ChatInteraction
import logging
import json
import time
import sys
import random

# 设置日志配置
logging.basicConfig(filename="chatgpt_C2Rust.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process(screenshots_path, projects_path, project, multi_conversation=False):
    chat_bot = ChatInteraction(screenshots_path)

    lang_pairs = os.listdir(projects_path)
    for lang_pair in lang_pairs:
        query_lang = "rust"
        corpus_lang = lang_pair.split("__")[1]

        questions_path = os.listdir(os.path.join(projects_path, lang_pair))
        for question_path in questions_path:
            # 如果存在表示已经计算过了
            # if os.path.exists(os.path.join("function_pair_by_gpt", project, lang_pair, question_path)) or os.path.exists(os.path.join("function_pair_by_gpt3.5", project, lang_pair, question_path)):
            if os.path.exists(os.path.join("function_pair_by_gpt4o", project, lang_pair, question_path)):
                logging.info(f"{lang_pair}的{question_path}已存在")
                continue

            with open(os.path.join(projects_path, lang_pair, question_path), 'r') as input_file:
                question = input_file.read()
                query_func = question[len("<Target function>\n"):question.find("</Target function>")]
                # print(query_func)
            
            while True:
                
            
                try:
                    # new_conversation = not multi_conversation or i == 0
                    message = f"""You are a professional who is expert in programming language {query_lang} and programming language {corpus_lang}.You will be provided with 1 Target function written in {query_lang} and 10 Possible matching functions written in {corpus_lang}(delimited with XML tags).Please select a function that has the same functionality as the Target function from 10 Possible matching functions.You should only response the serial number of the matching function or "None" if it doesn't exit.\n{question}"""
                    # message = f"""
                    # You are a professional who is expert in programming language {query_lang} and programming language {corpus_lang}.
                    # You will be provided with 1 Target function written in {query_lang} and 10 Possible matching functions written in {corpus_lang}(delimited with XML tags).
                    # Please select a function that has the same functionality as the Target function from 10 Possible matching functions.
                    # You should only response the serial number of the matching function or "None" if it doesn't exit.
                    # """

                    response = chat_bot.chat(message, new_conversation=True)
                    # response = 1
                    time.sleep(random.randint(3,5))
                    # df.at[i, 'answered'] = 'yes'
                    # df.to_csv(csv_path, index=False, encoding='utf-8')

                    logging.info(f"成功解决{lang_pair}的{question_path}")
                    # logging.info(f"回答: {response}")

                    # 保存回答
                    with open(os.path.join("function_pair_by_gpt4o", project, lang_pair, question_path), 'w') as output_file:
                        if response == "None":
                            output_file.write("None")
                        else:
                            start = question.find(f"<Function {response}>") + len("<Function {response}>\n")
                            end = question.find(f"</Function {response}>")
                            output_file.write(query_func)
                            output_file.write("------\n")
                            output_file.write(question[start:end])
                    break
                
                except StopIteration as e:
                    logging.error(f"获取{lang_pair}的{question_path}的回答时达到限额：{e}")
                    print(f"获取{lang_pair}的{question_path}的回答时发生达到限额：{e}\n请稍后重启")
                    sys.exit()

                except TimeoutError as e:
                    logging.error(f"获取{lang_pair}的{question_path}的回答时发生超时错误：{e}")
                    print(f"获取{lang_pair}的{question_path}的回答时发生超时错误：{e}")
                    time.sleep(5)
                
                except LookupError as e:
                    logging.error(f"获取{lang_pair}的{question_path}的回答时发生错误, 请求过长：{e}")
                    print(f"获取{lang_pair}的{question_path}的回答时发生错误， 请求过长：{e}")
                    with open(os.path.join("function_pair_by_gpt4o", project, lang_pair, question_path), 'w') as output_file:
                        output_file.write("message too long, skip this one")
                    break

                except Exception as e:
                    logging.error(f"处理问题{lang_pair}的'{question_path}' 时发生错误: {e}")
                    print(f"处理问题{lang_pair}的'{question_path}' 时发生错误: {e}")
                    time.sleep(5)
            

if __name__ == "__main__":
    screenshots_path = "./screenshots_4o"
    project = sys.argv[1]
    projects_path = "potential_function_pair/" + project # 替换为实际的文件路径
    process(screenshots_path, projects_path, project, multi_conversation=False)



### chat_interaction.py

import pyautogui
import time
import pyperclip
import argparse
import random
import math

class ChatInteraction:
    def __init__(self, screenshots_path):
        self.screenshots_path = screenshots_path

    def find_element(self, image_name, confidence=0.85):
        # 尝试找到屏幕上的元素
        if image_name=="response_ing.png":
            confidence=0.95
        if image_name=="error.png":
            confidence = 0.9
        # print(f"{self.screenshots_path}/{image_name}")
        try:
            location = pyautogui.locateCenterOnScreen(f"{self.screenshots_path}/{image_name}", confidence=confidence)       
            # print(location)
            return location
        except:
            raise Exception(f"Element {image_name} not found on screen.")

    def move_to_element(self, image_name):
        # 获取元素位置
        position = self.find_element(image_name)
        
        # 随机化移动速度
        duration = random.uniform(0.2, 0.3)
        pyautogui.moveTo(position, duration=duration)

    def click_element(self, image_name):

        # 点击屏幕上的元素
        time.sleep(0.1)
        self.move_to_element(image_name)
        pyautogui.click()
        time.sleep(0.25)

    def start_new_chat(self):
        # 开启新的长对话
        
        self.click_element("new_chat.png")

    def paste_and_send_text(self, text):
        # 点击消息框，粘贴文本并发送
        self.click_element("message_box.png")
        # 使用ctrl+v粘贴文本
        time.sleep(0.8)  # 等待剪贴板内容更新
        pyperclip.copy(text)
        time.sleep(0.8)  # 等待复制完成
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.8)  # 等待剪贴板内容更新
        pyautogui.press('enter')

    def wait_for_response(self, timeout=30):
        start_time = time.time()
        time.sleep(5)  # 等待一秒后再次检查
        type = True

        while True:
            # 生成的回复较多，需要手动拉到最底下才能找到复制的按钮
            try:
                self.click_element("new_page.png")
                time.sleep(3)
                type = False
            except:
                pass
            
            # 达到限额
            try:
                self.find_element("limit.png")
                return 3
            except:
                pass

            # 检查是否已经过了超时时间
            if time.time() - start_time > timeout:
                raise TimeoutError("Response timeout reached")

            # 出错
            try:
                # 出错原因为输入请求过长
                self.find_element("message_too_long.png")
                time.sleep(1)
                # 手动刷新页面，否则无法开启新会话
                self.click_element("refresh.png")
                time.sleep(3)
                return 2
            except:
                # 出错原因为过于频繁请求
                try:
                    self.find_element("error.png")
                    print("unusual activity, sleep 30s")
                    return 1
                except:
                    # 检测 response_ing.png 是否还在
                    try:
                        self.find_element("response_ing.png")
                        print("waiting")
                        pass  # 如果找到了元素，继续等待
                    except :
                        # 检测 response_end.png 是否出现
                        try:
                            self.find_element("response_end.png")
                            time.sleep(1)
                            # 查看是否生成的回复过长，需要多次生成
                            try:
                                self.click_element("continue_to_response.png")
                                start_time = time.time()
                            except:
                                return 0 #结束等待
                        except Exception:
                            pass  # 如果没有找到元素，继续等待

            time.sleep(1)  # 等待一秒后再次检查


    def copy_response(self, type):
        response_text="没有复制到回应内容"
        # 复制回应内容

        # 如果出现了换页情况，由于前面已经将鼠标移动到回答范围进行点击完成换页，就不需要再把鼠标移动到回答范围触发复制按钮的出现
        # 将鼠标从对话框移动到回答框触发复制按钮的出现
        # 选择角度从45°（π/4 弧度）到90°（π/2 弧度）之间的一个随机角度
        angle = math.pi / 2

        # 选择移动距离从100到200像素之间的一个随机值
        distance = random.randint(100, 200)

        # 计算x和y坐标的变化
        # x = distance * cos(angle)，y = distance * sin(angle)
        # 注意屏幕坐标系中y轴向下为正，向上移动需使用负值
        x_change = distance * math.cos(angle)
        y_change = -distance * math.sin(angle)

        # 执行鼠标移动
        pyautogui.moveRel(x_change, y_change)
        time.sleep(1)
        self.click_element("copy.png")
        time.sleep(1)  # 等待复制完成
        pyautogui.hotkey('ctrl', 'c')  # 复制到剪贴板
        time.sleep(1)  # 等待剪贴板内容更新
        response_text = pyperclip.paste() # 读取剪贴板内容
        print("copy completed")
        return response_text

    def send_text_and_get_response(self, text):
        try:
            self.paste_and_send_text(text)
        except:
            print("messagebox not found")
            self.find_element("error.png")
            print("unusual activity, sleep 30s")
            time.sleep(60)
            self.click_element("error.png")
        while True:
            type = self.wait_for_response()
            if type == 3:
                print("response limit")
                raise StopIteration("response limit")
            elif type == 2:
                print("message too long, skip this one")
                raise LookupError("message too long, skip this one")
            elif type == 1:
                time.sleep(60)
                self.click_element("error.png")
            else:
                break
        return self.copy_response(type)

    def continue_chat(self, text):
        response = self.send_text_and_get_response(text)
        return response

    def chat(self, text, new_conversation=True):
        try:
            if new_conversation:
                self.start_new_chat()
            response = self.continue_chat(text)
            return response
        except TimeoutError as e:
            # 特别处理超时异常
            raise e
        except LookupError as e:
            print(f"lookup error: {e}")
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e


# 把send_text设置为可解析的命令行参数
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--send_text", type=str, default="Hello, ChatGPT!")
    args = parser.parse_args()
    send_text = args.send_text

    # 使用示例
    screenshots_path = "./screenshots"  # 截图所在的文件夹路径
    chat_bot = ChatInteraction(screenshots_path)
    response = chat_bot.chat(send_text)  # 开始新对话
    print(response)

    # 继续当前对话
    follow_up_response = chat_bot.chat("Another question", new_conversation=False)
    print(follow_up_response)

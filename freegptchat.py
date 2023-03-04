import openai
import gradio as gr

# Syntax highlighting for the code snippets
import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

openai.api_key = "YOUR API KEY HERE"

chat_history = []
print("What kind of chatbot would you like to create?")
system_msg = "What type of chatbot would you like to create? " + input()

def highlight_code(code):
    # find code matches in markdown ```(.*?)``` and ```\n(.*?)\n``` and ```\n(.*?)``` and ```(.*?)\n```
    matches = re.findall(r"```(.*?)```", code, re.DOTALL)
    matches += re.findall(r"```(.*?)\n```", code, re.DOTALL)
    matches += re.findall(r"```\n(.*?)\n```", code, re.DOTALL)
    matches += re.findall(r"```\n(.*?)```", code, re.DOTALL)
    
    # replace each match with highlighted html
    for match in matches:
        # detect language
        lexer = get_lexer_by_name("python", stripall=True)
        # highlight code
        formatted_code = highlight(match, lexer, HtmlFormatter())
        # replace code with highlighted html
        code = code.replace("```" + match + "```", formatted_code)
        code = code.replace("```" + match + "\n```", formatted_code)
        code = code.replace("```\n" + match + "\n```", formatted_code)
        code = code.replace("```\n" + match + "```", formatted_code)

    return code


def gpt_reply(chat_history):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history)
    reply = response["choices"][0]["message"]["content"]
    return reply

def predict(input, history = []):
    if len(history) == 0:
        history.append({"role": "system", "content": system_msg})
    if len(history) > 10:
        history.pop(1)
        history.pop(2)
        history.pop(3)
    
    message = input
    history.append({"role": "user", "content": message})
    reply = gpt_reply(history)
    reply = highlight_code(reply)
    history.append({"role": "assistant", "content": reply})
    # create new list with only the user and bot responses
    # Each response is a string of one item of a list 
    # This took me absolutely ages to figure out because the API returns a dictionary
    # NOT a list of lists....
    chat_history.append([message, reply])
    return chat_history, history

with gr.Blocks(css="#chatbot .overflow-y-auto{height:700px!important}") as freeGPT:
    chatbot = gr.Chatbot(elem_id="chatbot")
    state = gr.State([])
    
    with gr.Row():
        txt = gr.Textbox(show_label=False, placeholder="Say hello to your new assistant, or ask it anything.").style(container=False)
    
    txt.submit(predict, [txt, state], [chatbot, state])

freeGPT.launch()

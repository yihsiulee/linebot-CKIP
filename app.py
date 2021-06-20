from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import requests
import tensorflow
from ckiptagger import WS, POS, NER, construct_dictionary
from bs4 import BeautifulSoup

app = Flask(__name__)


# Channel Access Token
line_bot_api = LineBotApi('8RDRlqTBPnpai7Mf/iRX7bvPrbzOlmSWZjOVyegT4XQM+TpsnO1wzruJfd6BGH/f+EZsKsFDUdmtAXD6EaoHlCJJ33el/4Dn9O9JU7pTlBYzHkQ9bAFdQeLvUEzgfSNKQxkllEHDriWRJDqA0SgP1AdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('f6517de47f7e678c32c2da64b650e462')

freeticket=[]
def reply():
    replyMessage = ''
    for i in range(len(freeticket)):
        replyMessage += '{}\n'.format(freeticket[i])
    return replyMessage

def test():
    a="hihihi"
    return a
def pttSoup():
    freeticket.clear()
    ws = WS("./data")
    # pos = POS("./data")
    # ner = NER("./data")

    word_to_weight = {"贈票": 10, "好雷": 10, "有雷": 10,
                      "微好雷": 10, "微雷": 10, "無雷": 10,
                      "極雷": 10, "無雷": 10}
    dictionary = construct_dictionary(word_to_weight)

    # 斷詞處理部分
    titleList = []
    hrefList = []


    # 爬蟲部分
    url = "https://www.ptt.cc/bbs/movie/index.html"
    for s in range(50):

        # 用request下載首頁內容
        r = requests.get(url)
        # 確認是否下載成功
        if r.status_code == requests.codes.ok:
            # 以 BeautifulSoup 解析 HTML 程式碼
            soup = BeautifulSoup(r.text, 'html.parser')

            div_tags = soup.find_all('div', {'class': 'title'})  # 找到網頁中全部的 <div class="title">
            for div_tag in div_tags:
                a_tag = div_tag.find('a')
                if a_tag is not None:  # 或文章被刪除會是None，所以要排除None

                    text = a_tag.text  # 抓出標題文字
                    titleList.append(text)
                    href = "https://www.ptt.cc" + a_tag.get('href')  # 抓出網址
                    hrefList.append(href)
                    # print(a_tag.text)
                    # print (href)

            upPage = soup.select("div.btn-group.btn-group-paging a")  # 會把這標籤底下的a都抓出來
            upHref = "https://www.ptt.cc" + upPage[1]["href"]
            # print (s,"上一頁是：",upHref)
            url = upHref

    # print (len(titleList))
    # print (len(hrefList))

    for r in range(len(titleList)):
        ws_results = ws([titleList[r]],
                        sentence_segmentation=True,  # To consider delimiters
                        segment_delimiter_set={"。", ":", "?", "!", ";", "[", "]"},  # Defualt delimiters
                        # recommend_dictionary = dictionary1, # words in this dictionary are encouraged
                        coerce_dictionary=dictionary)
        # pos_results = pos([text])
        # ner_results = ner([text], pos_results)
        # print (ws_results)
        # print (type(ws_results)) type-list

        for q in range(len(ws_results)):
            # print (ws_results)
            # print (ws_results[0][1])
            if ws_results[0][1] == "贈票":
                freeticket.append([titleList[r], hrefList[r]])
    print (freeticket)



@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body, "Signature: " + signature)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
       abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    print(msg)
    msg = msg.encode('utf-8')

    if event.message.text == '免費看':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="等等喔 我找找"))
        pttSoup()
    if event.message.text =="找到沒":
        a=reply()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=a))
    if event.message.text == '測試':
        a=test()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=a))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))

if __name__ == "__main__":
    app.run(debug=True,port=80)


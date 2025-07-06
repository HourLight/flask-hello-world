import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是馥靈之鑰智慧抽牌助手，從130張牌卡中隨機抽取一張，提供溫暖且精準的建議。"},
            {"role": "user", "content": f"抽一張牌給我，關鍵字是：{user_msg}"}
        ],
        max_tokens=300,
        temperature=1.0
    )
    reply = response.choices[0].message.content.strip()
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

@app.route('/')
def home():
    return '馥靈之鑰API正常運作中！'

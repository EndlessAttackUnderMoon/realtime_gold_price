from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api import AstrBotConfig
import requests

def get_url_info(apiUrl: str, apiKey: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 Edg/90.0.818.41",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    requestParams = {
        'key': apiKey,
        'v': ''}
    try:
        response = requests.get(apiUrl, headers=headers, params=requestParams)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None    

def get_au9999_data(resp_data):
    sub_data = resp_data["result"][0]
    for v in sub_data.values():
        if v["variety"] == "Au99.99":
            return v

@register("实时金价", "EndlessAttackUnderMoon", "获取实时金价。", "1.1")
class PluginRealtimeGoldPrice(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""

    @filter.command("实时金价")
    async def get_realtime_gold_price(self, event: AstrMessageEvent):
        """这是一个AstrBot的 实时金价 指令，可获取实时金价。""" # handler描述
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)

        text = ""
        try:
            apiKey = self.config['apiKey']
            if apiKey == None or apiKey == "":
                text = "配置错误!"
            else:
                apiUrl = "http://web.juhe.cn/finance/gold/shgold"
                resp_data = get_url_info(apiUrl, apiKey)
                if resp_data == None:
                    text = "请求失败呀，等会儿再试试吧!"
                else:
                    au9999_data = get_au9999_data(resp_data)
                    if bool(au9999_data) == False:        
                        text = "没有获取到数据呢，等会儿再试试吧!"
                    else:
                        text = f"查到Au99.99最新数据了哦\n最新价: {au9999_data['latestpri']}\n开盘价: {au9999_data['openpri']}\n最高价: {au9999_data['maxpri']}\n" + \
                            f"最低价: {au9999_data['minpri']}\n涨跌幅: {au9999_data['limit']}\n昨日收盘价: {au9999_data['yespri']}\n" + \
                            f"总成交量: {au9999_data['totalvol']}\n更新时间{au9999_data['time']}"
        except Exception as e:
            logger.error(f"请求失败: {str(e)}")
            text = "请求失败!"

        yield event.plain_result(text) # 发送一条纯文本消息

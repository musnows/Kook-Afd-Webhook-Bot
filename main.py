import json
import os
import traceback
import aiohttp

from khl import Bot,Message,Channel
from khl.card import CardMessage,Card,Module,Element,Types

from utils.gTime import getTime
from utils.file.files import bot,AfdWebhook,VipUserDict,config
from utils.file.fileManage import save_all_file
from utils.myLog import _log,logMsg
from utils import botVip

debug_ch:Channel
"""日志频道"""
kook_base_url = "https://www.kookapp.cn"
kook_headers = {f'Authorization': f"Bot {config['bot']['token']}"}

async def bot_offline():
    """下线机器人"""
    url = kook_base_url + "/api/v3/user/offline"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=kook_headers) as response:
            res = json.loads(await response.text())
            _log.debug(res)
    return res


# 每5分钟保存一次文件
@bot.task.add_interval(minutes=5)
async def save_file_task():
    try:
        await save_all_file()
    except:
        err_cur = f"ERR! [{getTime()}] [Save.File.Task]\n```\n{traceback.format_exc()}\n```"
        _log.exception("ERR in Save_File_Task")
        await bot.client.send(debug_ch, err_cur) # type: ignore

# 看看机器人活着不
@bot.command(name='alive',case_sensitive=False)
async def alive_cmd(msg:Message,*arg):
    logMsg(msg)
    await msg.reply(f"bot alive here")

# 获取vip剩余时间
@bot.command(name='vip',case_sensitive=False)
async def vip_cmd(msg:Message,*arg):
    logMsg(msg)
    try:
        if not await botVip.vip_ck(msg):
            return
        time_remain = botVip.vip_time_remain(msg.author_id)
        cm = await botVip.vip_time_remain_cm(time_remain)
        await msg.reply(cm)
    except:
        _log.exception(f"Err in vip")

# 获取vip列表
@bot.command(name='vip-l',case_sensitive=False)
async def vip_list_cmd(msg:Message,*arg):
    logMsg(msg)
    try:
        text = await botVip.fetch_vip_user()
        if not text:
            text="当前没有vip用户"
        cm = CardMessage(Card(Module.Section(Element.Text(text,Types.Text.KMD))))
        await msg.reply(cm)
    except:
        _log.exception(f"Err in vip-l")

# 测试你是否为vip
@bot.command(name='vip-test',case_sensitive=False)
async def vip_test_cmd(msg:Message,*arg):
    logMsg(msg)
    try:
        if await botVip.vip_ck(msg):
            cm = CardMessage(Card(Module.Section(Element.Text("您是vip！",Types.Text.KMD))))
            await msg.reply(cm)
    except:
        _log.exception(f"Err in vip-test")

# 商店
@bot.command(name='shop',case_sensitive=False)
async def shop_cmd(msg:Message,*arg):
    logMsg(msg)
    try:
        cm = CardMessage()
        c =Card(Module.Section(Element.Text("欢迎选购机器人Vip",Types.Text.KMD)))
        # -------------
        # vip商品1,周vip
        vip_item_link1 = "https://afdian.net/order/create?product_type=1&plan_id=9aea871c304911ed8ec452540025c377&sku=%5B%7B%22sku_id%22%3A%229aed6edc304911edbeb552540025c377%22,%22count%22%3A1%7D%5D"
        # 添加上自定义订单号的字符串
        vip_item_link1+= f"&custom_order_id={msg.author_id}:7"
        c.append(
            Module.Section(
                Element.Text("周vip", Types.Text.KMD),
                Element.Button("购买", vip_item_link1, Types.Click.LINK)))
        # -------------
        
        # vip商品2,月vip
        vip_item_link2 = "https://afdian.net/order/create?product_type=1&plan_id=ff2949022e9611ed89d452540025c377&sku=%5B%7B%22sku_id%22%3A%22ff2bb4f82e9611ed83ac52540025c377%22,%22count%22%3A1%7D%5D"
        # 添加上自定义订单号的字符串
        vip_item_link2+= f"&custom_order_id={msg.author_id}:30"
        c.append(
            Module.Section(
                Element.Text("月vip", Types.Text.KMD),
                Element.Button("购买", vip_item_link2, Types.Click.LINK)))
        
        cm.append(c)
        await msg.reply(cm,is_temp=True) # 临时消息，所以这个按钮只有当前用户可以点
    except:
        _log.exception(f"Err in shop")


@bot.command(name='kill')
async def KillBot(msg: Message,at_text="", *arg):
    logMsg(msg)
    try:
        if not at_text:
            return await msg.reply(f"必须at机器人才能下线 `/kill @机器人`")
        
        # 保存所有文件
        await save_all_file(False)
        await msg.reply(f"[KILL] 保存全局变量成功，bot下线")
        res = "webhook"
        if config['bot']['ws']:
            res = await bot_offline()  # 调用接口下线bot
        _log.info(f"KILL | bot-off: {res}\n")
        os._exit(0)  # 退出程序
    except:
        _log.exception(f"Err in kill")


@bot.on_startup
async def startup_task(bot:Bot):
    """启动任务"""
    try:
        global debug_ch
        debug_ch = await bot.client.fetch_public_channel(config['channel']['debug_ch'])
        _log.info(f"[BOT.START] fetch channel success")
    except:
        _log.exception(f"[BOT.START] Err")
        os.abort()

if __name__ == '__main__':
    _log.info(f"[BOT] start at {getTime()}")
    bot.run()
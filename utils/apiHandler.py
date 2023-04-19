import json
from khl.card import CardMessage,Card,Module,Element,Types

from .myLog import _log
from .file.files import AfdWebhook,config,bot
from .botVip import add_vip

def get_order_id_dict(custom_order_id:str)->dict:
    """解析custom_order_id"""
    index = custom_order_id.find(':')
    user_id = custom_order_id[:index]
    day = custom_order_id[index+1:]
    day = int(day)
    return {"uid":user_id,"day":day}

# 测试一下这个函数
# print(get_order_id_dict("1342354:30"))

async def afd_request(request):
    """爱发电webhook处理函数"""
    # 获取参数信息
    body = await request.content.read()
    params = json.loads(body.decode('UTF8'))
    # 插入到日志中
    global AfdWebhook
    if "data" not in AfdWebhook:
        AfdWebhook["data"] = []
    AfdWebhook['data'].append(params)
    # 构造text
    text = ""
    if 'plan_title' in params['data']['order']:
        text = f"商品 {params['data']['order']['plan_title']}\n"
    user_id = params['data']['order']['user_id'] # afd用户id
    user_id = user_id[0:6]
    text += f"用户 {user_id}\n"
    for i in params['data']['order']['sku_detail']:
        text += f"发电了{i['count']}个 {i['name']}\n"
    text += f"共计 {params['data']['order']['total_amount']} 猿\n"
    # 处理自定义订单编号
    if 'custom_order_id' in params['data']['order']:
        text += f"自定义订单ID {params['data']['order']['custom_order_id']}"
        # kook用户id:vip天数
        order_id = params['data']['order']['custom_order_id']
        order_id = get_order_id_dict(order_id)
        _log.info(f"[afd] {str(order_id)}")
        if 'user' not in AfdWebhook:
            AfdWebhook['user'] = {}
        if order_id['uid'] not in AfdWebhook['user']:
            AfdWebhook['user'][order_id['uid']] = {}
        # 配置信息
        AfdWebhook['user'][order_id['uid']][params['data']['order']['out_trade_no']] = {
            "days":order_id['day'],
            "plan_id":params['data']['order']['plan_id'],
            "plan_title":params['data']['order']['plan_title'],
            "amount":params['data']['order']['total_amount']
        }
        AfdWebhook.save()
        # 添加vip用户
        await add_vip(order_id['uid'],order_id['day'])
    else:
        _log.warning(f"[afd] no custom_order_id in afd webhook")

    # 将订单编号中间部分改为#
    trno = params['data']['order']['out_trade_no']
    trno_f = trno[0:8]
    trno_b = trno[-4:]
    trno_f += "####"
    trno_f += trno_b
    # 构造卡片
    cm = CardMessage()
    c = Card(Module.Header(f"爱发电有新动态啦！"), Module.Context(Element.Text(f"订单号: {trno_f}")), Module.Divider(),
             Module.Section(Element.Text(text, Types.Text.KMD)))
    cm.append(c)
    _log.debug(json.dumps(cm))
    # 发送到指定频道
    debug_ch = await bot.client.fetch_public_channel(config['channel']['debug_ch'])
    await bot.client.send(debug_ch, cm)
    _log.info(f"trno:{params['data']['order']['out_trade_no']} | afd-cm-send")
    # 返回状态码
    return {"ec": 200, "em": "success"}

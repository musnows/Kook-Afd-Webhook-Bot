import time
import copy
from typing import Union
from datetime import datetime,timedelta,timezone
from khl import Bot,Message
from khl.card import CardMessage,Card,Module,Element,Types

from .file.files import bot,VipUserDict,VipUser,_log

DAY_TIMES = 86400
"""24H in secons"""

def vip_time_remain(user_id)->float:
    """
    get time remain of vip, return in seconds
    """
    # 时间差值
    timeout = VipUserDict[user_id]['time'] - time.time()
    return timeout

async def vip_time_remain_cm(times):
    """获取vip时间剩余卡片消息"""
    cm = CardMessage()
    c1 = Card(color='#e17f89')
    c1.append(Module.Section(Element.Text('您的「vip会员」还剩', Types.Text.KMD)))
    c1.append(Module.Divider())
    c1.append(Module.Countdown(datetime.now() + timedelta(seconds=times), mode=Types.CountdownMode.DAY))
    cm.append(c1)
    return cm

def get_none_vip_cm():
    """card msg info user not vip"""
    c = Card(color='#e17f89')
    c.append(Module.Section(Element.Text("您并非vip用户", Types.Text.KMD)))
    cm = CardMessage(c)
    return cm

# 检查用户vip是否失效或者不是vip
async def vip_ck(msg:Union[Message,str])->bool:
    """
    params can be:
        * `msg:Message`   check & inform user if they aren't vip
        * `author_id:str` will not send reply, just check_if_vip 
    
    retuns:
        * True: is vip
        * False: not vip
    """
    # 判断是否为msg对象并获取用户id
    is_msg = isinstance(msg, Message)
    user_id = msg if not is_msg else msg.author_id
    cm = CardMessage() if not is_msg else get_none_vip_cm()

    # 检查
    if user_id in VipUserDict:
        # 用户的vip是否过期？
        if time.time() > VipUserDict[user_id]['time']:
            del VipUserDict[user_id]
            # 如果是消息，那就发送提示
            if is_msg:
                await msg.reply(cm)
                _log.info(f"[vip-ck] Au:{user_id} msg.reply | vip out of date")
            return False
        else:  #没有过期，返回真
            _log.info(f"[vip-ck] Au:{user_id} is vip")
            return True
    # 用户不是vip
    else:
        if is_msg:  #如果是消息，那就发送提示
            await msg.reply(cm)
            _log.info(f"[vip-ck] Au:{user_id} msg.reply | not vip")
        return False
    

async def add_vip(user_id:str,day:int,user_name=""):
    """
    - 提供用户id和天数，新增vip用户
    - 如果用户已存在，则添加vip时长
    """
    global VipUserDict
    if user_id not in VipUserDict:
        VipUserDict[user_id] ={"name":user_name,"time":time.time()}
    if not user_name:
        user = await bot.client.fetch_user(user_id)
        VipUserDict[user_id]["name"] = f"{user.username}#{user.identify_num}"
    # time字段是初始化vip时间+剩余时间，也就是vip时间截止的时间戳
    VipUserDict[user_id]["time"] += day * DAY_TIMES
    _log.info(f"[vip-add] Au:{user_id} | day:{day} | time:{VipUserDict[user_id]['time']}")
    

async def fetch_vip_user():
    """获取当前vip用户列表（这会剔除过期vip）"""
    global VipUserDict,VipUser
    vipuserdict_temp = copy.deepcopy(VipUserDict)
    text = ""
    for u, ifo in vipuserdict_temp.items():
        if await vip_ck(u):  # vip-ck会主动修改dict
            time = vip_time_remain(u)
            time = format(time / DAY_TIMES, '.2f')
            # 通过/86400计算出大概的天数
            text += f"{u}_{ifo['name']}\t = {time}\n"

    if vipuserdict_temp != VipUserDict:
        #将修改存放到文件中
        VipUser.save()
        _log.info(f"[vip-r] update VipUserDict")

    return text
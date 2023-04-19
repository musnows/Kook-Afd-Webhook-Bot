from .fileManage import FileManage
from ..myLog import _log

# 配置相关
config = FileManage("./config/config.json", True) 
"""机器人配置文件"""
AfdWebhook = FileManage("./log/AfdWebhook.json")
"""爱发电的wh请求"""

# vip相关
VipUser = FileManage("./log/VipUser.json")
"""vip 用户列表/抽奖记录"""
VipUserDict = VipUser['data']
"""vip 用户列表"""

# 实例化一个khl的bot，方便其他模组调用
from khl import Bot,Cert
bot = Bot(token=config['bot']['token'])  # websocket
"""main bot"""
if not config['bot']['ws']:  # webhook
    bot = Bot(cert=Cert(token=config['bot']['token'],
                        verify_token=config['bot']['verify_token'],
                        encrypt_key=config['bot']['encrypt']),
              port=config['bot']['webhook_port'])  # webhook
"""main bot"""
_log.info(f"Loading all files") # 走到这里代表所有文件都打开了
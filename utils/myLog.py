import logging # 采用logging来替换所有print
LOGGER_NAME = "botlog"
LOGGER_FILE = "bot.log"

# 只打印info以上的日志（debug低于info）
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s:%(filename)s:%(funcName)s:%(lineno)d | %(message)s",
                    datefmt="%y-%m-%d %H:%M:%S")
# 获取一个logger对象
_log = logging.getLogger(LOGGER_NAME)
# 实例化控制台handler和文件handler，同时输出到控制台和文件
# cmd_handler = logging.StreamHandler() # 默认设置里面，就会往控制台打印信息;自己又加一个，导致打印俩次
file_handler = logging.FileHandler(LOGGER_FILE, mode="a", encoding="utf-8")
fmt = logging.Formatter(fmt="[%(asctime)s] %(levelname)s:%(filename)s:%(funcName)s:%(lineno)d | %(message)s",
                    datefmt="%y-%m-%d %H:%M:%S")
file_handler.setFormatter(fmt)
_log.addHandler(file_handler)


# 在控制台打印msg内容，用作日志
from khl import Message,PrivateMessage
def logMsg(msg: Message) -> None:
    try:
        # 系统消息id，直接退出，不记录
        if msg.author_id == "3900775823":return
        # 私聊用户没有频道和服务器id
        if isinstance(msg, PrivateMessage):
            _log.info(
                f"PrivateMsg | Au:{msg.author_id} {msg.author.username}#{msg.author.identify_num} | {msg.content}")
        else:
            _log.info(
                f"G:{msg.ctx.guild.id} | C:{msg.ctx.channel.id} | Au:{msg.author_id} {msg.author.username}#{msg.author.identify_num} = {msg.content}"
            )
    except:
        _log.exception("Exception occurred")
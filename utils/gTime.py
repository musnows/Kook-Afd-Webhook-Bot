from datetime import datetime,timedelta,timezone

def getTime(format_str='%y-%m-%d %H:%M:%S'):
    """获取当前时间，默认格式为 `23-01-01 00:00:00`"""
    utc_dt = datetime.now(timezone.utc) # 获取当前时间
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8))) # 转换为北京时间
    return bj_dt.strftime(format_str)

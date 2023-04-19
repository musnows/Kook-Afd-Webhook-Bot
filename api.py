import json
from aiohttp import web

from utils.gTime import getTime
from utils.myLog import _log
from utils.apiHandler import afd_request

# 初始化节点
routes = web.RouteTableDef()


# 基础返回
@routes.get('/')
async def hello_world(request):  # put application's code here
    _log.info(f"request | root-url")
    return web.Response(body=json.dumps(
        {
            'code': 0,
            'message': f'Hello! Get recv at {getTime()}'
        },
        indent=2,
        sort_keys=True,
        ensure_ascii=False),
                        status=200,
                        content_type='application/json')


# 爱发电的wh
@routes.post('/afd')
async def aifadian_webhook(request):
    _log.info(f"request | /afd")
    try:
        ret = await afd_request(request)
        return web.Response(body=json.dumps(ret, indent=2, sort_keys=True, ensure_ascii=False),
                            content_type='application/json')
    except:
        _log.exception("Exception in /afd")
        return web.Response(body=json.dumps({
            "ec": 0,
            "em": "err ouccer"
        }, indent=2, sort_keys=True, ensure_ascii=False),
                            status=503,
                            content_type='application/json')




app = web.Application()
app.add_routes(routes)
if __name__ == '__main__':
    try: # host需要设置成0.0.0.0，否则只有本地才能访问
        HOST,PORT = '0.0.0.0',14726
        _log.info(f"API Service Start at {HOST}:{PORT}")
        web.run_app(app, host=HOST, port=PORT)
    except:
        _log.exception("Exception occur")
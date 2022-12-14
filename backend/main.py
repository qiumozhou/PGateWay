from aiohttp import web
import aiohttp
from db.db_session import select, insert, update, delete
import aiohttp_cors
from utils.utils import ip_limit,number_limit
from log.log import  logger
import json



"""微服务地址,根据实际情况修改"""
SERVER = "127.0.0.1:8080"


"""路由转发函数"""
async def fetch(request,session, url):
    try:
        headers = {"Content-Type": "application/json"}
        async with session.request(request.method,json=await request.json(),url=url,headers=headers) as response:
            return {"code": 10000,"data":json.loads(await response.text())["data"]}
    except:
        return {"code": 10006,"msg":"微服务异常"}

"""预处理函数"""
async def pre_handle(service_name,request):
    if request.content_type != "application/json":
        return {"code": "100010", "data": "暂不支持非json格式数据"}
    else:
        """根据微服务名称查找微服务地址及端口"""
        result = await select("gateway_mapping",["host"],{"service_name":service_name})
        if result["code"]==10000 and result["data"]:
            host = result["data"][0]['host']
            target_url = str(request.url).replace(SERVER + '/' + service_name, host)
            async with aiohttp.ClientSession() as session:
                response = await fetch(request, session, target_url)
            return response
        else:
            return {"code": "100011", "data": "未找到该微服务-{}".format(service_name)}


@web.middleware
async def before_request(request,handler):
    service_name = str(request.url).split('/')[3]
    if service_name == "gateway":
        return await handler(request)
    else:
        """黑名单处理逻辑"""
        ip = request.host.split(':')[0]
        result =await ip_limit(ip,service_name)
        if result:
            return web.json_response({'data': result})
        """频次限制逻辑"""
        result = number_limit(service_name)
        if result:
            return web.json_response({'data': result})
        response =await pre_handle(service_name,request)
        return web.json_response({'data':response})


app = web.Application(middlewares=[before_request])


routes = web.RouteTableDef()

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
})


@routes.post("/gateway/findAll")
async def gateway_query(request):
    try:
        json_data = await request.json()
        logger.info(json_data)
        offset,limit = json_data["offset"],json_data['limit']
    except:
        return web.json_response({'code': "100200", 'msg':"请求参数错误"})
    result =await select("gateway_mapping",["id","number","service_name","host","create_time","update_time","black_list"],{},offset,limit)
    return web.json_response(result)


@routes.post("/gateway/create")
async def gateway_create(request):
    try:
        dict_data = await request.json()
        logger.info(dict_data)
    except:
        return web.json_response({'code': "100200", 'msg':"请求参数错误"})
    result = await insert("gateway_mapping",dict_data)
    return web.json_response(result)


@routes.post("/gateway/update")
async def gateway_update(request):
    try:
        dict_data = await request.json()
        logger.info(dict_data)
    except:
        return web.json_response({'code': "100200", 'msg':"请求参数错误"})
    result = await update("gateway_mapping",dict_data["id"],dict_data)
    return web.json_response(result)


@routes.post("/gateway/delete")
async def gateway_delete(request):
    try:
        dict_data = await request.json()
        logger.info(dict_data)
    except:
        return web.json_response({'code': "100200", 'msg':"请求参数错误"})
    result = await delete("gateway_mapping",dict_data["id"])
    return web.json_response(result)


app.router.add_routes(routes)


for route in list(app.router.routes()):
    cors.add(route)


if __name__ == "__main__":
    web.run_app(app)
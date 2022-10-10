import time
from multiprocessing.dummy import Pool

from botoy import Action, FriendMsg, S
from botoy import async_decorators as deco
from botoy import jconfig
from botoy.schedule import scheduler

import Func

func = Func.CSGO()
pool = Pool(10)
"""CSGO饰品监控机器人
饰品功能命令列表：\n饰品添加+饰品分享链接，心理预期价位(可不填)\n饰品查询\n饰品删除+饰品分享链接
项目官网请访问：https://skin.laosepi.cool"""

action = None


@deco.ignore_botself
@deco.startswith("饰品")
async def receive_friend_msg(ctx: FriendMsg):
    try:
        global action
        if action is None:
            action = Action(
                jconfig.qq, host=getattr(ctx, "_host"), port=getattr(ctx, "_port")
            )
        CMD = ctx.Content[2:4].strip()  # 获取关键字
        url = ctx.Content[4:].strip()  # 获取分享链接
        abc = {"a": 1}
        if CMD == "添加":
            if url.isspace() or len(url) == 0 or "[ATALL()]" in url:
                await S.atext("饰品功能命令列表：\n饰品添加+饰品分享链接，心理预期价位(可不填)\n饰品查询\n饰品删除+饰品分享链接")
            else:
                res = func.Ins_Url(QQ=ctx.FromUin, url=url)
                if type(res) == type(abc):
                    text = "%s\n上架平台：%s\n当前价格：%s" % (
                        res["name"],
                        res["market"],
                        res["price"],
                    )
                    await S.aimage(res["img"], text=text)
                elif res == "G":
                    await S.atext("该饰品已下架!")
                elif res == "D":
                    await S.atext("您已添加过该商品！")
                elif res == "O":
                    await S.atext("已达饰品存储上限！更多储存空间请选择自建接口或赞助作者！")
        elif CMD == "删除":
            if func.Del_Url(ctx.FromUin, url):
                await S.atext("已删除该饰品!")
            else:
                await S.atext("哦呀，数据库里妹有这个饰品呢~")
        elif CMD == "查询":
            Stamp, code = func.sqlc.execute(
                "SELECT LastLogin, ChkAPI from ids where QQ = %d" % ctx.FromUin
            ).fetchone()
            if (
                time.time() - Stamp >= 600 and code is not None
            ) or code is None:  # 间隔大于十分钟
                code = func.Create_API(ctx.FromUin)
                url = str(jconfig.WebAPI) + str(code)
                await S.atext("芜湖~\n访问链接：%s\n有效期半小时，请勿泄露给他人哦~" % url)
            else:
                url = str(jconfig.WebAPI) + str(code)
                await S.atext("请勿在短时间内多次请求哦~\n访问链接：%s" % url)
        else:
            await S.atext("饰品功能命令列表：\n饰品添加+饰品分享链接\n饰品查询\n饰品删除+饰品分享链接")
    except Exception:
        await S.atext("饰品功能命令列表：\n饰品添加+饰品分享链接\n饰品查询\n饰品删除+饰品分享链接")


@scheduler.scheduled_job("interval", minutes=jconfig.interval)
def _():
    # lasted new
    if action is not None:
        Data = func.Get_All_links()
        power = [pool.map(func.Up_Url, Data)][0]
        t = 0
        for res in power:
            if res["flag"] == 0:  # 饰品两次查询均为下架状态
                action.sendFriendText(
                    res["QQ"],
                    "您关注的：%s\n已下架或售出，已在数据库中删除该链接：%s"
                    % (res["name"], res["url"].replace('"', "")),
                )
                func.Del_Url(res["QQ"], res["url"].replace('"', ""))
            elif res["flag"] == 1:  # 更新数据
                func.sqlc.execute(
                    "UPDATE links set (NowPrice, ChkTime, Status) = (%f, %d, %d) where QQ = %d and link = %s"
                    % (res["price"], res["time"], res["status"], res["QQ"], res["url"])
                )
                action.sendFriendText(
                    res["QQ"],
                    "您关注的：%s\n发生价格波动，当前价格为%s\n购买链接：%s"
                    % (res["name"], res["price"], res["url"].replace('"', "")),
                )
            elif res["flag"] == 2:  # 只更新时间
                func.sqlc.execute(
                    "UPDATE links set ChkTime = %d where QQ = %d and link = %s"
                    % (res["time"], res["QQ"], res["url"])
                )
            elif res["flag"] == 3:  # 更新出售状态但不提示
                func.sqlc.execute(
                    "UPDATE links set (ChkTime, Status) = (%d, %d) where QQ = %d and link = %s"
                    % (res["time"], res["status"], res["QQ"], res["url"])
                )
            t += 1
            if t == 50:
                t = 0
                func.conn.commit()
            elif 50 >= len(power) == t:
                func.conn.commit()

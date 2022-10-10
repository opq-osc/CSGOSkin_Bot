import asyncio
import json

from botoy import AsyncBotoy, FriendMsg, jconfig
from botoy.decorators import equal_content, ignore_botself
from botoy.sugar import Text

bot = AsyncBotoy(
    host=str(jconfig.host),
    port=int(jconfig.port),
    log=True,
    log_file=True,
    use_plugins=True,
)


@bot.friend_context_use
def friend_ctx_middleware(ctx: FriendMsg):
    ctx.QQ = ctx.FromUin  # 这条消息的发送者
    if ctx.MsgType == "TempSessionMsg":  # 临时会话
        ctx.Content = json.loads(ctx.Content)["Content"]
        ctx.type = "temp"
        ctx.QQG = ctx.TempUin
    else:
        ctx.type = "friend"  # 好友会话
        ctx.QQG = 0
    return ctx


@bot.on_group_msg
@bot.on_friend_msg
@ignore_botself
@equal_content("帮助")
def help(_):
    Text(bot.plugMgr.help)


if __name__ == "__main__":
    asyncio.run(bot.run())

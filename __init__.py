"""插件帮助信息"""
from botoy import Action, GroupMsg, S
from botoy import decorators as deco
from botoy.contrib import plugin_receiver

try:
    # 如果需要用到单独插件测试运行，请这样处理项目中所有的导入操作
    from .core import say_hello
except ImportError:
    from core import say_hello


@plugin_receiver.group
@deco.ignore_botself
def group(ctx: GroupMsg):
    S.text(say_hello(ctx.FromNickName))
    Action.from_ctx(ctx)

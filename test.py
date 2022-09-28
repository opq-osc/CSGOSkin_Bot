if __name__ == "__main__":
    # 辅助开发，直接运行 python test.py 然后编辑插件代码
    # 或者就把项目作为插件放在你的机器人中测试也行
    from botoy import Botoy, run

    import __init__ as plugin

    # 这里需要修改, 建议设置环境变量 BOTOY_HOST, BOTOY_PORT
    bot = Botoy(host=None, port=None)
    g_r = plugin.__dict__.get("receive_group_msg")
    f_r = plugin.__dict__.get("receive_friend_msg")
    e_r = plugin.__dict__.get("receive_events")
    if g_r:
        bot.on_group_msg(g_r)
    if f_r:
        bot.on_friend_msg(f_r)
    if e_r:
        bot.on_event(e_r)

    run(bot, True)

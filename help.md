## 0x00 简介

这里简要分析四个饰品交易平台的分享链接构成以及饰品信息获取方法。

### 1.Buff分享链接

Buff的分享链接型如：`https://buff.163.com/market/m/item_detail?classid=2735398489&contextid=2&goods_id=45266&instanceid=480085254&assetid=25304597888&game=csgo&sell_order_id=220919T2012735091`

![](https://s2.loli.net/2022/09/28/Po1tAO2cs8xHg6q.png)

上图中蓝色字的皮肤编号对应的是皮肤的某个磨损，型如：AK-47 | 血腥运动（崭新出厂）→00001，AK-47 | 血腥运动（略有磨损）→00002...是一个固定的值，且每个平台的皮肤ID都不一样，不可修改；图中的X1和X2暂时没有弄清楚有什么用，但是应该是用来查询商家信息和订单信息的；X3是皮肤的解析视图ID，可以修改，但修改后将无法正常获取饰品的解析视图；X4是`分享时间+订单编号`的格式，这里就涉及到了对皮肤的删除操作，如果想删除一个Buff的饰品，则需要先使用`饰品查询`命令，进入饰品列表复制最开始创建时使用的链接，否则使用新链接将无法匹配对应的饰品。

然后进行一个简单的抓包，可以发现饰品的参数是直接通过网页传递的，那么使用requests+bs4获取并解析网页获取信息即可。

![](https://s2.loli.net/2022/09/28/81cPW6KtGuSx5ZI.png)

### 2.IGXE分享链接

IGXE的分享链接型如：`/share/trade/272204254?app_id=730`

非常的简洁，就一个参数，那么这个肯定就是订单编号了，但是可以注意到后面还有一个`app_id`，其参数为730，如果细心一点就会发现其实在其他几家的饰品信息中都会出现这个`730`，他是什么呢？打开CSGO的Steam页面就明白了：https://store.steampowered.com/app/730/CounterStrike_Global_Offensive/ ；可以注意到这里的链接里面就有一个`/app/730`，所以730就代表了CSGO在Steam游戏库中的ID。

然后简单的抓包分析一下，这里可以发现有一个单独的请求用于获取饰品的信息，且返回信息为Json格式，那就非常的舒服了，requests获取json信息，json库处理文本即可得到全部信息。

![](https://s2.loli.net/2022/09/28/fWdEgpPJeUKjyzn.png)

### 3.悠悠有品

悠悠有品的分享链接型如：`/goodsInfo.html?id=16652333`

也是只有一个参数，那么肯定就是订单编号了。简单的进行一下抓包分析，不难发现，返回的数据信息同上面的IGXE的接口几乎相同，也只需要简单的处理一下就可以得到想要的数据了。

![](https://s2.loli.net/2022/09/28/Fud8vjGtbkPNY2C.png)

### 4.小黑盒

小黑盒的分享链接型如：`https://api.xiaoheihe.cn/mall/trade/sku/page?sku_id=25965777356&is_share=1`

这里面最主要的一个参数还是`sku_id`，很明显也是订单号，也没什么好说的，简单抓个包看看，也可以找到对应的返回数据，同样的简单处理一下即可得到想要的数据。

![](https://s2.loli.net/2022/09/28/jRlzNpH6ufkgVtI.png)

### 5.代理池

由于以前有过爬Buff差点被封号的经历，所以这次就加入了代理池的部分，在获取数据的时候使用代理服务器，能有效的避免出现被BanIP的情况。

本项目使用的是芝麻代理：https://www.zmhttp.com/ ，主要就是看中他每天可以白嫖20个免费IP，如果我们仅使用get方法获取数据的话是不会消耗使用次数的，变相可以无限白嫖。

下面简单介绍一下代理池脚本工作原理：

#### 01 自动获取每日免费IP

由于代理池的免费IP需要手动领取，那么为了程序持久化运行必然就需要一个能够自动领取IP的功能。

登录自己的账号，简单的抓包分析一下：

首先是登录，在登录时会向`https://uwapi.http.linkudp.com/index/users/login_do`接口提交登录的表单信息，然后在领取IP的时候是向`https://owapi.http.linkudp.com/index/users/get_day_free_pack`接口提交一个全为空值的表单，即可领取当天的免费IP。

首先我们构造一个Session，使用Session直接使用明文提交数据到登录接口（~~这里批评一下，不太安全~~），然后系统将会生成一个SessionID，我们直接将SessionID装载进我们的Session中，然后将空表单提交到白嫖接口，即可实现白嫖。下面放一下代码：

```python
def zm_login(phone, pwd):
	"""
	白嫖芝麻代理

	:param phone: 账号
	:param pwd: 密码
	:return:
	"""
	zm_url = "https://uwapi.http.linkudp.com/index/users/login_do"  # 登录接口
	bp_url = 'https://owapi.http.linkudp.com/index/users/get_day_free_pack'  # 白嫖接口
	headers = {
		'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
	}
	Session = requests.session()  # 生成Session保持会话
	data = {
		'phone': phone,
		'password': pwd,
		'remember': 1
	}
	res = Session.post(zm_url, data=data, headers=headers).json()['ret_data']  # 登录账号，获取当前SessionID
	bp_data = {
		'geetest_challenge': None,
		'geetest_validate': None,
		'geetest_seccode': None
	}
	# 接口为Post方式，但无需数据，故提交空表
	s_head = {
		'session-id': res,
		'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
	}
	return Session.post(bp_url, data=bp_data, headers=s_head)  # 提交数据进行白嫖
```

#### 02 获取代理并进行预处理

在领取了免费代理后即可使用官方API获取代理信息，这里我们提取数量选择1即可，数据格式选择Json格式，省份混拨，其他的默认就好，然后点击生成按钮即可获取API。

> 注意：在获取API后需将运行脚本的客户端IP添加进白名单才能正常请求

![](https://s2.loli.net/2022/09/28/h2EQ3azKWjVZlkf.png)

由于芝麻的接口限制了QPS为1，并且我们也不需要太过频繁的切换IP，设置了两个全局变量，一个是上次请求的时间，一个是上次请求的代理IP，通过判断当前时间和请求时间的时间间隔，来决定是否需要重新获取IP。

```python
def Chk_Price(self, url):
    """
		获取代理发起请求，避免被锁IP，检测饰品价格

		:param url: 饰品链接
		:return: 返回信息见 Sw_Mkt()函数
		"""
    ...
    nowTime = time.time()
    if nowTime - self.LastGet >= 30:  # 当前时间距上次请求时间过去了30秒
        zm_API = API  # 芝麻的API
        res = json.loads(requests.get(zm_API).text)  # get接口获取IP代理
        code = res['code']
        if code == 0:  # 正常获取代理
            self.LastGet = nowTime
            IP_data = res['data']
            for ips in IP_data:
                proxymeta = str(ips["ip"]) + ':' + str(ips["port"])
                self.IP = {"http": proxymeta}
                return Sw_Mkt(url, self.IP)
        else:  # 获取失败，可能是到了第二天，那么重新登录并领取白嫖套餐
            Tmp_DB = [phone, pwd]  # 芝麻账号密码
            phone = Tmp_DB[0]
            pwd = Tmp_DB[1]
            zm_login(phone, pwd)  # 尝试自动登录并领取白嫖套餐
            return self.Chk_Price(url)  # 重新执行当前Url，并跳过数值检查
    else:
        return Sw_Mkt(url, self.IP)  # 不到30秒，直接使用之前的IP访问
```

## 0x01 安装

本项目为[OPQ-Bot](https://github.com/opq-osc/OPQ)的插件项目，使用[Botoy](https://github.com/opq-osc/botoy)框架进行开发

### 1.安装OPQ-Bot

由于官方Wiki已给出十分完整的安装指南，这里将不再赘述。

传送门：[https://github.com/opq-osc/OPQ/wiki/安装指南](https://github.com/opq-osc/OPQ/wiki/%E5%AE%89%E8%A3%85%E6%8C%87%E5%8D%97)

### 2.安装CSGOSkin_Bot

首先需要安装Python环境，本项目开发时使用的是Python3.9.6，如果新版本Python无法正常运行可尝试安装[此版本](https://www.python.org/downloads/release/python-396/)。

下载或克隆本项目到硬盘中，并进入项目所在目录



执行命令`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

或`pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`



等所有的进度条都走完以后，进入`botoy.json`文件修改机器人配置



配置文件的第二行`port`处填写OPQ-Bot运行的端口号，如果没有修改过端口号则无需修改；在`qq`和`admin`处填写机器人的QQ号和你的QQ号，**请勿填反**，否则将无法正常运行！并修改其中的`web_api`为你的域名，形如`http://www.sample.com/`，**这里最后的一个/不能省略**！

配置文件填写妥当后，进入控制台执行命令`python bot.py`，待机器人插件载入后发送命令测试机器人功能是否正常。

> 注：若使用海外服务器部署bot可能会无法正常工作，因为芝麻代理的免费API不能使用海外IP访问；Bot启动后，将在**第一次接收到命令后**开始定时并执行查询数据库中保存的饰品数据。



测试bot功能均正常后，可利用Screen等工具使程序持续化运行。

> 注：饰品查询功能需配合下一步的API接口一起使用，否则将无法正常运行！

### 3.安装配套API

建议在完成上一步操作后进行此项操作，如果选择自建的方式则这一步为必须的操作，否则将无法查询已保存的饰品记录。

首先需要确保设备安装有Python环境，执行命令`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`（若在第二步已执行过此命令则可跳过）



待所有依赖安装完成后，进入`Bot_API.py`文件，在最下面一行找到`app.run(debug=False, port=7355, threaded=True)`，可根据自己的情况修改端口号，并使用反向代理等方法通过域名访问。



进入控制台执行命令`python Bot_API.py`



此时可运行机器人以及机器人插件，观察机器人功能是否正常，若正常即可利用Screen等工具使程序持续化运行。

## 0x02 Q&A

> 本段上次更新时间为：2022年9月28日

1. Q：我如果用你搭建好的机器人会收费么？
   A：本项目完全免费，普通用户拥有10个饰品储存位，限制数量的原因是节省机器资源（~~球富婆包养买更好的服务器555~~），如果需要更多的储存位可联系我进行Py。
2. Q：为什么我看到皮肤价格发生变化了但是Bot没有提示？
   A：目前设定的检测频率为**30分钟一次**，并不是实时监测的；如果自行搭建可在`botoy.json`配置文件中进行修改，但不建议评论过快，容易导致程序发生错误。目前Bot的检测逻辑为：皮肤价格发生变化，则立即提醒；皮肤状态发生变化（售出或下架），第一次检测到后仅存入数据库，不提示，第二次检测仍为售出或下架，则删除皮肤在数据库中的链接，并发送提示。
   ![](https://s2.loli.net/2022/09/28/XZ4YB7pNLEw9yFc.png)
3. Q：可以监控悠悠有品中别人出租的饰品的租期么？
   A：这一点目前做不到，在订单返回信息中仅能获取当前订单情况（出售或下架），无法获知饰品具体去向。
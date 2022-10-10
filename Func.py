import requests
import sqlite3
import time
import re
from bs4 import BeautifulSoup as bs
import json
from hashlib import md5 as MD
from botoy import jconfig


def get_uu(url, IP):
	good_id = re.findall(r'=(.*)', url)[0]
	API = 'https://h5.youpin898.com/api/commodity/Commodity/Detail?Id=' + str(good_id)
	status = 0
	res = requests.get(API, proxies=IP).json()
	res = res["Data"]
	if res['Status'] == 20:  # 饰品状态，
		status = 1
	try:
		biaoqian = res['NameTags'][0]
	except TypeError:
		biaoqian = ''
	try:
		img = 'https://youpin.img898.com/' + res['Images'].split(',')[0]
	except AttributeError:
		img = res['ImgUrl']
	data = {
		"name": res['CommodityName'],
		"biaoqian": biaoqian,
		"muban": "图案模版(paint seed): " + str(res['PaintSeed']),
		"bianhao": "皮肤编号(paint index):" + str(res['PaintIndex']),
		"mosun": res['Abrade'],
		"price": res['Price'],
		"img": img,
		"status": status,
		"market": "UU"
	}
	return data


def get_buff(url, IP):
	res = requests.get(url, proxies=IP).text
	soup = bs(res, 'html.parser')
	footer = soup.find('div', class_='good-detail-footer')
	try:
		h_6 = footer.find('h6')
		span = h_6.find('span').text
		price = span.split(' ')[1]
		img = soup.find('img', class_='show_inspect_img').get('src')
		info = soup.find('div', class_='title-info-wrapper')
		name = info.find('h3').text
		Ps = info.find_all('p')
		biaoqian = info.find('p', class_='name_tag')
		status = 1
		if biaoqian == None:
			muban = Ps[0].text
			bianhao = Ps[1].text
			mosun = Ps[2].text.replace('磨损:', '')
		else:
			biaoqian = biaoqian.text
			muban = Ps[1].text
			bianhao = Ps[2].text
			mosun = Ps[3].text.replace('磨损:', '')
	except AttributeError:
		price = ''
		img = ''
		name = ''
		muban = ''
		mosun = ''
		biaoqian = ''
		bianhao = ''
		status = 0
	data = {
		"name": name,
		"muban": muban,
		"bianhao": bianhao,
		"mosun": mosun,
		"price": price,
		"img": img,
		"biaoqian": biaoqian,
		"status": status,
		"market": "Buff"
	}
	return data


def get_ig(url, IP):
	good_id = re.findall(r'trade/(.*)\?', url)[0]
	API = 'https://www.igxe.cn/app-h5/data/730/' + good_id + '?type=1'
	res = requests.get(API, proxies=IP).json()['data']
	biaoqian = res['fraudwarnings']
	status = res['status']
	if status:
		status = 1
	if biaoqian:
		biaoqian = biaoqian[0]
	else:
		biaoqian = None
	data = {
		"name": res['market_name'],
		"biaoqian": biaoqian,
		"muban": "图案模版(paint seed): " + str(res['paint_seed']),
		"bianhao": "皮肤编号(paint index):" + str(res['paint_index']),
		"mosun": res['wear'],
		"price": res['unit_price'],
		"img": res['inspect_img_large'],
		"status": status,
		"market": "Igxe"
	}
	return data


def get_xhh(url, IP):
	good_id = re.findall(r'id=(.*)&', url)[0]
	API = 'https://api.xiaoheihe.cn/mall/trade/sku/info?os_type=webinapp&app=heybox&client_type=mobile&version=1.3.231&x_client_type=web&x_os_type=Android&x_app=heybox&sku_id=' + str(
		good_id)
	res = requests.get(API, proxies=IP).json()['result']
	status = 0
	if 'price' in res:
		status = 1
		price = res['price']
	else:
		price = 0
	data = {
		"name": res['name'],
		"biaoqian": '',
		"muban": res['attrs'][0],
		"bianhao": res['attrs'][1],
		"mosun": res['float_value'].replace('磨损:', ''),
		"price": price,
		"img": res['full_img_url'],
		"status": status,
		"market": "Xhh"
	}
	return data


def Sw_Mkt(trade_url, IP):
	"""
	判断输入链接所在平台，调用对应的检测函数

	:param trade_url: 饰品链接
	:param IP: 代理池IP
	:return:  饰品数据
	"""
	if 'youpin' in trade_url:
		return get_uu(trade_url, IP)
	elif 'buff' in trade_url:
		return get_buff(trade_url, IP)
	elif 'igxe' in trade_url:
		return get_ig(trade_url, IP)
	elif 'xiaoheihe' and 'sku_id' in trade_url:
		return get_xhh(trade_url, IP)


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


class CSGO:
	def __init__(self):
		self.db = './test1.db'  # 设置数据库文件位置
		self.conn = sqlite3.connect(self.db, check_same_thread=False)  # 初始化数据库连接
		self.sqlc = self.conn.cursor()  # 创建一个cursor
		self.Mon = 2592000  # 一个月的秒数
		self.HalfHour = 1800  # 半个小时
		self.notVipLim = 10  # 非会员限制链接数：10
		self.VipLim = 50  # 会员链接数：50
		self.LastGet = 0.0
		self.IP = {}
		self.phone = jconfig.phone
		self.pwd = jconfig.pwd

	def Chk_QQ(self, QQ):
		"""
		检查QQ号在数据库中是否存在及会员信息等

		:param QQ: QQ号，整数
		:return: 0：不存在，反之则返回账号具体信息
		"""
		cursor = self.sqlc.execute("SELECT *  from ids where QQ=%d" % QQ).fetchone()  # 查询是否存在指定QQ号
		if cursor is not None:
			self.sqlc.execute("UPDATE ids SET LastLogin = %d where QQ=%d" % (int(time.time()), QQ))  # 更新账户最后登录时间
			self.conn.commit()
			return cursor
		else:
			return 0

	def Create_QQ(self, QQ):
		"""
		创建账户，默认非VIP，更新登录时间为当前

		:param QQ: 传入用户QQ号
		:return: 1：创建成功；0：数据库已有数据
		"""
		if not self.Chk_QQ(QQ):  # 再次检验账号状态
			self.sqlc.execute(
				"INSERT into ids (QQ, VIP, VipTime, LastLogin) VALUES (%d, 0, -1, %d)" % (QQ, int(time.time())))
			self.conn.commit()
			return 1
		else:
			return 0

	def Ins_Url(self, QQ, url, ExcPrice=-1.0):
		"""
		新建查询条目

		:param QQ: 用户QQ
		:param url: 饰品链接
		:param ExcPrice: 用户预期价位，默认-1
		:return: data：操作成功，便于后期发出通知；D：有相同链接；O：达到账户链接数限制；G：皮肤已下架
		"""
		Furl = '\"' + url + '\"'  # 需要注意的是url需要符合形如：\'https://www.baidu.com\'，方可正确执行Sql命令
		Info = self.Chk_QQ(QQ)
		flag = 0  # 插入标志符
		lnk_count = self.sqlc.execute("SELECT count(link)  from links where QQ=%d" % QQ)  # 统计用户储存链接数
		if Info:  # 查询用户组
			if Info[1] == 0:  # 非会员
				for row in lnk_count:
					if row[0] <= self.notVipLim:
						flag = 1
			elif Info[1] == 1:  # 会员
				for row in lnk_count:
					if row[0] <= self.VipLim:
						flag = 1
			elif Info[1] == 2:  # 自建外部API
				...
		else:
			self.Create_QQ(QQ)
			return self.Ins_Url(QQ, url, ExcPrice)
		if flag:
			same_link = self.sqlc.execute("SELECT count(link) from links where QQ=%d and link=%s" % (QQ, Furl))
			for row in same_link:
				if row[0] == 0:  # 无重复链接
					data = self.Chk_Price(url)
					NPrice = float(data['price'])
					Name = '\'' + data['name'] + '\''
					MoSun = float(data['mosun'])
					market = '\'' + data['market'] + '\''
					status = data['status']
					if status:
						self.sqlc.execute(
							"INSERT into links (QQ, link, Market, Weapon, MoSun, UpTime, UpPrice, NowPrice, ChkTime, ExcPrice, Status) VALUES (%d, %s, %s, %s, %f, %d, %f, %f, %d, %f, %d)" % (
								QQ, Furl, market, Name, MoSun, int(time.time()), NPrice, NPrice, int(time.time()),
								ExcPrice,
								status))
						self.conn.commit()
						return data  # Success insert 成功插入
					else:
						return 'G'  # Goods off the shelf 商品下架
				else:
					return 'D'  # Duplicate link 重复链接
		else:
			return 'O'  # Out of account limit 超出账户限制链接数

	def Up_Url(self, Data):
		"""
		更新饰品信息，每个用户一个线程操作，检测到下架饰品将在数据库中删除并返回被删除饰品链接

		:param Data:  传入参数，顺序为饰品链接、上次检测价格、上次检测状态、用户QQ号
		:return:  返回用户QQ
		"""
		url = Data[0]
		Furl = '\"' + url + '\"'
		data = self.Chk_Price(url)
		UpPrice = Data[1]
		status = data['status']
		QQ = Data[3]
		NPrice = 0
		Name = Data[4]
		flag = 1
		if not status:  # 本次查询结果为下架
			Pstatus = Data[2]
			if not Pstatus:  # 上次查询结果为下架
				flag = 0
			else:
				flag = 3
		else:
			NPrice = float(data['price'])
			if NPrice != UpPrice:  # 只有当饰品价格发生变动
				flag = 1
			elif NPrice == UpPrice:  # 只更新时间
				flag = 2
		res = {
			'flag': flag,  # 0为下架，1为更新价格、状态和时间，2为仅更新时间，3为更新出售状态
			'price': NPrice,
			'time': int(time.time()),
			'QQ': QQ,
			'url': Furl,  # 直接返回处理过的数据，避免二次处理
			'status': status,
			'name': Name
		}  # 返回数据list
		return res  # 返回数据集

	def Chk_Price(self, url):
		"""
		获取代理发起请求，避免被锁IP，检测饰品价格

		:param url: 饰品链接
		:return: 返回信息见 Sw_Mkt()函数
		"""
		...
		nowTime = time.time()
		if nowTime - self.LastGet >= 30:
			zm_API = 'http://webapi.http.zhimacangku.com/getip?num=1&type=2&pro=0&city=0&yys=0&port=1&pack=234772&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
			res = json.loads(requests.get(zm_API).text)  # get接口获取IP代理
			code = res['code']
			if code == 0:  # 正常获取代理
				self.LastGet = nowTime
				IP_data = res['data']
				for ips in IP_data:
					proxymeta = str(ips["ip"]) + ':' + str(ips["port"])
					self.IP = {"http": proxymeta}
				return Sw_Mkt(url, self.IP)
			else:  # 获取失败
				Tmp_DB = [self.phone, self.pwd]
				phone = Tmp_DB[0]
				pwd = Tmp_DB[1]
				zm_login(phone, pwd)  # 尝试自动登录并领取白嫖套餐
				return self.Chk_Price(url)  # 重新执行当前Url，并跳过数值检查
		else:
			return Sw_Mkt(url, self.IP)  # 不到10秒，直接使用之前的IP访问

	def Del_Url(self, QQ, url):
		flag = self.sqlc.execute("select * from links where QQ=%d and link=%s" % (QQ, '\''+url+'\'')).fetchone()
		if flag:
			self.sqlc.execute("Delete from links where link=%s and QQ=%d" % ('\''+url+'\'', QQ))
			self.conn.commit()
			return 1
		else:
			return 0

	def Create_API(self, QQ):
		"""
		根据QQ号和当前时间戳生成临时API短代码

		:param QQ: 用户QQ
		:return:
		"""
		md = MD()
		md.update(str(QQ).encode('utf-8'))
		# Stamp = self.sqlc.execute('Select LastLogin from ids where QQ = %d' % QQ).fetchone()[0]
		Stamp = time.time()
		Chk_API = '\'' + md.hexdigest() + hex(int(Stamp)) + '\''
		self.sqlc.execute(
			'UPDATE ids set (LastLogin, ChkAPI) = (%d, %s) where QQ = %d' % (int(Stamp), Chk_API, QQ))
		self.conn.commit()
		return md.hexdigest() + hex(int(Stamp))

	def Chk_API(self, Code: str):
		"""
		校验接口传入API短代码

		:param Code: API传入的短代码
		:return: 0：短代码不存在或已过期；1：短代码可用
		"""
		try:
			QQ = self.sqlc.execute('SELECT QQ from ids where ChkAPI = %s' % ('\'' + Code + '\'')).fetchone()[0]
			Stamp = Code.split('x')[1]
		except Exception:
			return 0
		if int(time.time()) - int(Stamp, 16) <= self.HalfHour:
			return QQ
		else:
			self.sqlc.execute('UPDATE ids set ChkAPI = \'\' where QQ = %d' % QQ)
			self.conn.commit()
			return 0

	def Get_data(self, Code):
		QQ = self.sqlc.execute('SELECT QQ from ids where ChkAPI=%s' % ('\'' + Code + '\'')).fetchone()[0]
		datas = self.sqlc.execute('SELECT * from links where QQ = %d' % QQ).fetchall()
		res = {
			'code': 0,
			'data': []
		}
		for data in datas:
			tmp = {
				"creat_time": data[5],
				"isSold": data[10],
				"market": data[2],
				"name": data[3],
				"now_price": data[7],
				"price_on_mark": data[6],
				"update_time": data[8],
				"url": data[1]
			}
			res['data'].append(tmp)
		return res

	def Get_All_links(self):
		return self.sqlc.execute("SELECT link, NowPrice, Status, QQ, Weapon from links").fetchall()


if __name__ == "__main__":
	S = CSGO()
	API = '511872942eb2358a3ed024c6bee3d2150x63296627'
	print(S.Chk_API(API))

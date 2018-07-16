from urllib.parse import urlencode

from django.conf import settings


class OAuthQQ(object):
	"""用于qq登录的工具类,生成相应的url等"""

	def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
		self.client_id = client_id or settings.QQ_CLIENT_ID
		self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
		self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
		self.state = state or settings.QQ_STATE  # 用于保存登录成功后的跳转页面路径

	def generate_qq_login_url(self):
		"""生成用于qq登录扫码的url地址"""
		params = {
			'response_type': 'code',
			'client_id': self.client_id,
			'redirect_uri': self.redirect_uri,
			'state': self.state,
			'scope': 'get_user_info',  # 用户勾选的授权范围,get_user_info表示,获取登录用户的昵称、头像、性别
		}
		url = 'https://graph.qq.com/oauth2.0/authorize?'
		# 拼接查询字符串,
		url += urlencode(params)
		return url

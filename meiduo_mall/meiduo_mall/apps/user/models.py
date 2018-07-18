from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer

# Create your models here.
from meiduo_mall.utils.exceptions import logger
from meiduo_mall.utils.models import BaseModel


class User(AbstractUser):
	"""用户模型"""
	mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
	email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

	# 默认地址
	default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
										on_delete=models.SET_NULL, verbose_name='默认地址')

	class Meta:
		db_table = 'tb_users'
		verbose_name = '用户'
		verbose_name_plural = verbose_name

	def generate_mobile_token(self):
		"""
		使用手机号生成token
		TimedJSONWebSignatureSerializer()可以生成对象
		该对象可以使用.dump()生成带有时效的token,bytes类型
		"""
		serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
		# data = token中的载荷
		data = {'mobile': self.mobile}
		token = serializer.dumps(data).decode()
		return token

	def generate_password_token(self):
		"""使用user.id生成token"""
		serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
		# data = token中的载荷
		data = {'user_id': self.id}
		token = serializer.dumps(data).decode()
		return token

	@staticmethod
	def check_access_token_send_sms(token):
		"""校验access_token获取真实的当前用户mobile"""
		serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
		try:
			data = serializer.loads(token)
		except Exception as e:
			logger.error('解析mobile异常%s' % e)
			return None
		else:
			return data.get('mobile')

	@staticmethod
	def check_access_token_reset_password(user_id, token):
		"""校验access_token获取真实的当前用户mobile"""
		serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
		try:
			data = serializer.loads(token)
		except Exception as e:
			logger.error('解析user_id异常%s' % e)
			return False
		else:
			if user_id != str(data.get('user_id')):
				return False
			else:
				return True

	def generate_email_url(self):
		"""生成发送email使用的url"""
		serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
		data = {
			'user_id': self.id,
			'email': self.email,
		}
		access_token = serializer.dumps(data).decode()
		url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + access_token
		return url

	@staticmethod
	def check_verify_email_token(token):
		"""
		检查验证邮件的token
		"""
		serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 300)
		try:
			data = serializer.loads(token)
		except Exception as e:
			logger.error(e)
			return None
		else:
			email = data.get('email')
			user_id = data.get('user_id')
			try:
				user = User.objects.get(id=user_id, email=email)
			except User.DoesNotExist:
				return None
			else:
				return user


class Address(BaseModel):
	"""收货地址"""
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
	title = models.CharField(max_length=20, verbose_name='地址名称')
	receiver = models.CharField(max_length=20, verbose_name='收货人')
	province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses',
								 verbose_name='省')
	city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
	district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses',
								 verbose_name='区')
	place = models.CharField(max_length=50, verbose_name='地址')
	mobile = models.CharField(max_length=11, verbose_name='手机')
	tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
	email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
	is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')
	# 指定定义管理器
	objects = models.Manager()

	class Meta:
		db_table = 'tb_address'
		verbose_name = '用户地址'
		verbose_name_plural = verbose_name
		ordering = ['-update_time']

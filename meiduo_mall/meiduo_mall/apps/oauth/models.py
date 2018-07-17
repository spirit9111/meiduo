from django.db import models

# Create your models here.

from django.db import models
from meiduo_mall.utils.models import BaseModel


class OAuthQQUser(BaseModel):
	"""QQ登录的模型"""
	user = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name='用户')
	openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)
	objects = models.Manager()

	class Meta:
		db_table = 'tb_oauth_qq'
		verbose_name = 'QQ登录用户数据'
		verbose_name_plural = verbose_name

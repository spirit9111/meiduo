from django.db import models


class BaseModel(models.Model):
	"""积累模型"""
	create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
	update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

	class Meta:
		# abstract表示不会创建真实的模型
		abstract = True

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from django_redis import get_redis_connection
# 返回图片验证码

# GET image_code/(?P<image_code_id>)
from apps.verifications.constants import IMAGE_CODE_REDIS_EXPIRES
from libs.captcha.captcha import captcha


class ImageColdView(APIView):
	"""图片验证码接口"""

	def get(self, request, image_code_id):
		text, image = captcha.generate_captcha()
		redis_conn = get_redis_connection('verify_codes')
		redis_conn.setex('img_%s' % image_code_id, IMAGE_CODE_REDIS_EXPIRES, text)
		return HttpResponse(image, content_type='image/jpg')

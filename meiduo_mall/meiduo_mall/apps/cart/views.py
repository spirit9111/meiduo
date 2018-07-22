import base64
import pickle

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.serializers import AddSkuSerializer, CartSKUSerializer
from goods.models import SKU
from meiduo_mall.utils.exceptions import logger


class CartView(APIView):
	"""购物车添加接口"""

	def perform_authentication(self, request):
		# 推迟身份验证行为
		# 在request.user时进行首次验证
		pass

	# 购物车 增
	# 参数 selected/sku_id/count, request.data
	def post(self, request):
		# 校验参数,取出参数备用
		serializer = AddSkuSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		sku_id = serializer.validated_data.get('sku_id')
		count = serializer.validated_data.get('count')
		selected = serializer.validated_data.get('selected')

		# 判断用户的登录状态,
		try:
			user = request.user
		except Exception as e:
			logger.error(e)
			user = None
		# 如果user存在且能通过验证,就视为已经登录
		if user is not None and user.is_authenticated:
			# 已登录将购物车数据保存到,redis
			# 数据的格式hash/list

			# sku_id 和 count
			# {
			# 	user:{sku_id1:count1,sku_id2:count2}
			# },

			# sku_id和selected
			# {
			# 	user:[sku_id1,sku_id2...]
			# }
			redis_conn = get_redis_connection('cart')
			pl = redis_conn.pipeline()
			pl.hincrby('cart_%s' % user.id, sku_id, count)
			if selected:
				pl.sadd('cart_selected_%s' % user.id, sku_id)
			pl.execute()
			return Response(serializer.data, 201)
		else:
			# 未登录将购物车数据保存到,cookie
			# 数据结构
			# {
			# sku_id:{
			# 	'count':count,
			# 	'selected':True or False
			# },
			# ...
			# }
			# 从cookie中取出可能已有的cart数据进行修改
			cart = request.COOKIES.get('cart')
			if cart is not None:
				# 将cookie中的字符串编码成byte类型,b'xxx'
				# 然后base64解码成二进制,b'01x/...'
				# 最后转为python字典
				cart = cart.encode()
				cart = base64.b64decode(cart)
				cart = pickle.loads(cart)
			else:
				cart = {}

			# 判断原有的购物车中是否已经存在该商品
			# 如果存在修改数量
			sku = cart.get(sku_id)
			if sku:
				count += int(sku.get('count'))

			cart[sku_id] = {
				'count': count,
				'selected': selected
			}

			# 最后编码成str设置到cookie中保存
			cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
			response = Response(serializer.data, 201)
			response.set_cookie('cart', cookie_cart, max_age=365 * 24 * 60 * 60)
			return response

	# 购物车 查
	def get(self, request):
		# 判断用户的登录状态,
		try:
			user = request.user
		except Exception as e:
			logger.error(e)
			user = None
		# 如果已经登录从redis中查询
		if user is not None and user.is_authenticated:
			redis_conn = get_redis_connection('cart')
			# 分别查询两张表,byte类型
			sku_id_count_dict = redis_conn.hgetall('cart_%s' % user.id)
			selected_list = redis_conn.smembers('cart_selected_%s' % user.id)
			# 调整
			cart = {}
			for sku_id, count in sku_id_count_dict.items():
				cart[int(sku_id)] = {
					'selected': sku_id in selected_list,
					'count': int(count),
				}

		# 没有登录从cookie中查询
		else:
			cart_cookie = request.COOKIES.get('cart')
			if cart_cookie is not None:
				cart = pickle.loads(base64.b64decode(cart_cookie.encode()))
			else:
				cart = {}
		# 返回数据给前端
		sku_query_set = SKU.objects.filter(id__in=cart.keys())
		for sku in sku_query_set:
			# 再返回的数据中新增不在model中的额外字段
			sku.count = cart[sku.id]['count']
			sku.selected = cart[sku.id]['selected']

		serializer = CartSKUSerializer(sku_query_set, many=True)
		return Response(serializer.data)

# 购物车 改
# 购物车 删

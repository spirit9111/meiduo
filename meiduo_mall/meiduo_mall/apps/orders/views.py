from decimal import Decimal

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from orders.serializers import OrderSettlementSerializer


class OrderShowView(APIView):
	"""展示商品订单信息"""
	permission_classes = [IsAuthenticated, ]

	# 从redis_cart中获取已勾选的数据
	def get(self, request):
		user = request.user
		redis_conn = get_redis_connection('cart')
		# {sku_id:count,...}
		# [sku_id,...]
		redis_cart_dict = redis_conn.hgetall('cart_%s' % user.id)
		redis_cart_set = redis_conn.smembers('cart_selected_%s' % user.id)
		# 只需要获取已勾选的sku的数据
		cart = {}
		for sku_id in redis_cart_set:
			cart[int(sku_id)] = int(redis_cart_dict[sku_id])
		# 查询已勾选商品的具体信息
		sku_query_set = SKU.objects.filter(id__in=redis_cart_set)
		for sku_obj in sku_query_set:
			sku_obj.count = cart[sku_obj.id]
		# 运费
		freight = Decimal('10.00')
		data_dict = {
			'freight': freight,
			'skus': sku_query_set
		}
		serializer = OrderSettlementSerializer(data_dict)
		return Response(serializer.data)

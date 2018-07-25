from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from meiduo_mall.utils.exceptions import logger
from orders.models import OrderInfo, OrderGoods


class OrderShowSerializer(serializers.ModelSerializer):
	count = serializers.IntegerField(label='数量')

	class Meta:
		model = SKU
		fields = ('id', 'name', 'default_image_url', 'price', 'count')


class OrderSettlementSerializer(serializers.Serializer):
	"""
	订单结算数据序列化器
	"""
	freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
	skus = OrderShowSerializer(many=True)


# 最终返回的数据结构如下:
# {
#     "freight":"10.00",
#     "skus":[
#         {
#             "id":10,
#             "name":"华为 HUAWEI P10 Plus 6GB+128GB 钻雕金 移动联通电信4G手机 双卡双待",
#              "default_image_url":"http://image.meiduo.site:8888/group1/M00/00/02/CtM3BVrRchWAMc8rAARfIK95am88158618",
#             "price":"3788.00",
#             "count":1
#         },
#         {
#             "id":16,
#             "name":"华为 HUAWEI P10 Plus 6GB+128GB 曜石黑 移动联通电信4G手机 双卡双待",
#             "default_image_url":"http://image.meiduo.site:8888/group1/M00/00/02/CtM3BVrRdPeAXNDMAAYJrpessGQ9777651",
#             "price":"3788.00",
#             "count":1
#         }
#     ]
# }


class SaveOrderSerializer(serializers.ModelSerializer):
	"""提交订单"""

	class Meta:
		model = OrderInfo
		fields = ['order_id', 'address', 'pay_method', ]
		read_only_fields = ('order_id',)
		extra_kwargs = {
			'address': {
				'write_only': True,
				'required': True,
			},
			'pay_method': {
				'write_only': True,
				'required': True
			}
		}

	def create(self, validated_data):
		"""保存订单"""
		# 获取user_id
		user = self.context['request'].user
		# 生成order_id,时间戳+user.id
		order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
		# 获取address
		address = validated_data['address']
		# 获取pay_method
		pay_method = validated_data['pay_method']

		# 开启事务
		with transaction.atomic():
			# 创建保存点
			save_id = transaction.savepoint()
			try:
				# 保存数据到OrderInfo表
				order_obj = OrderInfo.objects.create(
					order_id=order_id,
					user=user,
					address=address,
					total_count=0,
					total_amount=Decimal(0),
					freight=Decimal(10),
					pay_method=pay_method,
					status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
						'CASH'] else
					OrderInfo.ORDER_STATUS_ENUM['UNPAID']
				)
				# 保存数据到OrderGoods
				redis_conn = get_redis_connection('cart')
				redis_cart_hash = redis_conn.hgetall("cart_%s" % user.id)
				redis_cart_set = redis_conn.smembers('cart_selected_%s' % user.id)

				cart = {}
				# {sku_id:count,sku_id:count,...}
				for sku_id in redis_cart_set:
					count = redis_cart_hash[sku_id]
					cart[int(sku_id)] = int(count)

				sku_query_set = SKU.objects.filter(id__in=cart.keys())
				for sku_obj in sku_query_set:
					# 判断库存是否充足
					while True:
						sku_count = cart[sku_obj.id]  # 订单中的count
						sku_origin = SKU.objects.get(id=sku_obj.id)  # 每次都需要查询数据库中实时的数据
						# sku_count_origin = sku_obj.stock
						sku_count_origin = sku_origin.stock  # 数据库中的实时的count
						# sku_sales_origin = sku_obj.sales
						sku_sales_origin = sku_origin.sales  # 数据库中的实时的sales
						if sku_count > sku_count_origin:
							transaction.savepoint_rollback(save_id)
							raise serializers.ValidationError('库存不足')
						# import time
						# time.sleep(5)
						# 减少数据库的库存,增加销量
						new_stock = sku_count_origin - sku_count
						new_sales = sku_sales_origin + sku_count
						# 使用乐观锁,在更新时增加条件
						# 判断此时库存的数量是否已经改变
						# 如果已经改变,表示同一时间其他用户进行了数据库操作,需要重新判断库存
						ret = SKU.objects.filter(id=sku_obj.id, stock=sku_count_origin).update(stock=new_stock,
																							   sales=new_sales)
						if ret == 0:
							continue
						sku_obj.stock = new_stock
						sku_obj.sales = new_sales
						sku_obj.save()
						# 获取total_count
						order_obj.total_count += sku_count
						# 获取total_amount
						order_obj.total_amount += (sku_count * sku_obj.price)
						# 创建OrderGoods
						OrderGoods.objects.create(
							order=order_obj,
							sku=sku_obj,
							count=sku_count,
							price=sku_obj.price,
						)
						break
				# 增加运费,更新总价
				order_obj.total_amount += order_obj.freight
				order_obj.save()
			except serializers.ValidationError:
				raise
			except Exception as e:
				print(111)
				logger.error(e)
				transaction.savepoint_rollback(save_id)
				raise
			transaction.savepoint_commit(save_id)
			# 订单提交成功,cart中移除相应的商品
			redis_conn.hdel('cart_%s' % user.id, *redis_cart_set)
			redis_conn.srem('cart_selected_%s' % user.id, *redis_cart_set)
			return order_obj
# 获取status,根据支付方式显示不同的状态(待支付/待发货)

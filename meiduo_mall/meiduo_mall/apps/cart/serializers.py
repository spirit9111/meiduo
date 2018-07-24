from rest_framework import serializers

from goods.models import SKU
from meiduo_mall.utils.exceptions import logger


class AddSkuSerializer(serializers.Serializer):
	"""校验购物车参数"""
	sku_id = serializers.IntegerField(min_value=1)
	count = serializers.IntegerField(min_value=1)
	selected = serializers.BooleanField(default=True)

	def validate(self, data):
		try:
			sku = SKU.objects.get(id=data['sku_id'])
		except Exception as e:
			logger.error(e)
			raise serializers.ValidationError('商品不存在')

		if data['count'] > sku.stock:
			raise serializers.ValidationError('商品库存不足')

		return data


class CartSKUSerializer(serializers.ModelSerializer):
	count = serializers.IntegerField()
	selected = serializers.BooleanField()

	class Meta:
		model = SKU
		fields = ['id', 'name', 'default_image_url', 'price', 'count', 'selected', ]


class DeleteCartSeralizer(serializers.Serializer):
	sku_id = serializers.IntegerField(min_value=1)

	def validate_sku_id(self, value):
		try:
			SKU.objects.get(id=value)
		except Exception as e:
			logger.error(e)
			raise serializers.set_value('商品不存在')
		return value


class CartSelectSerializer(serializers.Serializer):
	selected = serializers.BooleanField(label='全选')

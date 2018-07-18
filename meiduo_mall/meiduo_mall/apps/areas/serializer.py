from rest_framework import serializers

from areas.models import Area


class AreaSerializer(serializers.ModelSerializer):
	"""省级序列化器"""

	class Meta:
		model = Area
		fields = ('id', 'name')


class SubAreaSerializer(serializers.ModelSerializer):
	"""市区级序列化器"""
	# 指定外键的展示/返回的形式
	subs = AreaSerializer(many=True, read_only=True)

	class Meta:
		model = Area
		fields = ('id', 'name', 'subs')

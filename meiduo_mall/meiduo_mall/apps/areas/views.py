from django.shortcuts import render

# Create your views here.
# 省市区三级联动
from rest_framework.viewsets import ReadOnlyModelViewSet
from areas.models import Area
from areas.serializer import AreaSerializer, SubAreaSerializer


class AreaView(ReadOnlyModelViewSet):

	def get_queryset(self):
		if self.action == 'list':
			# 省级,查询集
			return Area.objects.filter(parent=None)
		else:
			# 市区,查询集
			return Area.objects.all()

	def get_serializer_class(self):
		if self.action == 'list':
			return AreaSerializer
		else:
			return SubAreaSerializer

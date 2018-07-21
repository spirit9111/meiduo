from django.contrib import admin

# Register your models here.
from . import models


# 重写admin后台提交和修改删除等功能
# 目的是实现 在保存修改添加时 自动 异步生成新的详情界面

class SKUAdmin(admin.ModelAdmin):
	"""商品的新增"""

	def save_model(self, request, obj, form, change):
		obj.save()
		from celery_tasks.html.tasks import generate_static_sku_detail_html
		generate_static_sku_detail_html.delay(obj.id)


class SKUSpecificationAdmin(admin.ModelAdmin):
	"""商品规格的增删"""

	def save_model(self, request, obj, form, change):
		obj.save()
		from celery_tasks.html.tasks import generate_static_sku_detail_html
		generate_static_sku_detail_html.delay(obj.sku.id)

	def delete_model(self, request, obj):
		sku_id = obj.sku.id
		obj.delete()
		from celery_tasks.html.tasks import generate_static_sku_detail_html
		generate_static_sku_detail_html.delay(sku_id)


class SKUImageAdmin(admin.ModelAdmin):
	"""图片增删"""

	def save_model(self, request, obj, form, change):
		obj.save()
		from celery_tasks.html.tasks import generate_static_sku_detail_html
		generate_static_sku_detail_html.delay(obj.sku.id)

		# 设置SKU默认图片
		sku = obj.sku
		if not sku.default_image_url:
			sku.default_image_url = obj.image.url
			sku.save()

	def delete_model(self, request, obj):
		sku_id = obj.sku.id
		obj.delete()
		from celery_tasks.html.tasks import generate_static_sku_detail_html
		generate_static_sku_detail_html.delay(sku_id)


admin.site.register(models.GoodsCategory)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU, SKUAdmin)
admin.site.register(models.SKUSpecification, SKUSpecificationAdmin)
admin.site.register(models.SKUImage, SKUImageAdmin)

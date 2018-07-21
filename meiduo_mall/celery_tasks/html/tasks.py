import os

from django.conf import settings
from django.template import loader

from goods.models import SKU
from goods.utils import get_categories


def generate_static_sku_detail_html(sku_id):
	"""生成商品详情页的静态页面"""
	# 生成商品分类
	categories = get_categories()

	sku = SKU.objects.get(id=sku_id)
	# 获取导航栏的数据,面包屑
	goods = sku.goods
	goods.channel = goods.category1.goodschannel_set.all()[0]
	# 获取商品规格的参数id(红/白,7p/13p)
	sku_specs = sku.skuspecification_set.order_by('spec_id')
	sku_key = []
	for spec in sku_specs:
		# 取到规格相应的选项的内容参数id
		sku_key.append(spec.option.id)

	# 获取商品(spu)的全部规格(颜色,尺寸)
	skus = goods.sku_set.all()
	spec_sku_map = {}
	for s in skus:
		s_specs = s.skuspecification_set.order_by('spec_id')
		key = []
		for spec in s_specs:
			key.append(spec.option.id)
		spec_sku_map[tuple(key)] = s.id
	# {
	# 	([颜色,尺寸],): sku_1,
	# 	([],): sku_2,
	# }

	specs = goods.goodsspecification_set.order_by('id')
	# 若当前sku的规格信息不完整，则不再继续
	if len(sku_key) < len(specs):
		return
	for index, spec in enumerate(specs):
		# 复制当前sku的规格键
		key = sku_key[:]
		# 该规格的选项
		options = spec.specificationoption_set.all()
		for option in options:
			# 在规格参数sku字典中查找符合当前规格的sku
			key[index] = option.id
			option.sku_id = spec_sku_map.get(tuple(key))

		spec.options = options

	# 渲染模板，生成静态html文件
	context = {
		'categories': categories,
		'goods': goods,
		'specs': specs,
		'sku': sku
	}

	template = loader.get_template('detail.html')
	html_text = template.render(context)
	file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'goods/' + str(sku_id) + '.html')
	with open(file_path, 'w') as f:
		f.write(html_text)

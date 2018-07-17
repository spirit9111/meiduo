from django.conf import settings
from django.core.mail import send_mail

from celery_tasks.main import celery_app


@celery_app.task(name='send_to_email')
def send_to_email(to_email, verify_url):
	subject = "美多商城邮箱验证"
	html_message = '<p>尊敬的用户您好！</p>'
	html_message += '<p>感谢您使用美多商城。</p>'
	html_message += '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' % to_email
	html_message += '<p><a href="%s">%s<a></p>' % (verify_url, verify_url)
	# django自带的send_mail
	send_mail(subject, "", settings.EMAIL_FROM, [to_email], html_message=html_message)


# send_to_email('1020186996@163.com', '111111')

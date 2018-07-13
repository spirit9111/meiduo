from celery_tasks.main import celery_app
from celery_tasks.sms.dysms_python.send_2_mes import SendMes


@celery_app.task(name='send_to_mes')
def send_to_mes(phone, mes_code):
	# try:
	print(11111)
	send_sms = SendMes()
	send_sms.send_2_mes(phone, mes_code)
	# except Exception as e:
	# logger.error(e)

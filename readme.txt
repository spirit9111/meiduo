redis 开启方式
sudo redis-server /etc/redis/redis.conf

前端服务器开启方式
在front_pc_pc下执行     live-server

celery开启方式
在meiduo_mall下执行     celery -A celery_tasks.main worker -l info


docker run -dti --network=host --name tracker -v /var/fdfs/tracker:/var/fdfs delron/fastdfs tracker


docker run -dti --network=host --name storage -e TRACKER_SERVER=192.168.246.144:22122 -v /var/fdfs/storage:/var/fdfs delron/fastdfs storage
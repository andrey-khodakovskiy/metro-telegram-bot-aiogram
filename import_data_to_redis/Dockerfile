FROM python:3.8.6
WORKDIR /import-to-redis-pod
COPY . .
RUN pip install -r requirements.txt
CMD python import_data_to_redis.py
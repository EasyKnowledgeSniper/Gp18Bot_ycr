FROM python
COPY chatbot.py .
COPY requirements.txt .
COPY mountains.json .
RUN pip install pip update
RUN pip freeze > requirements.txt
RUN pip install -r requirements.txt
RUN pip install python-telegram-bot==13.7
RUN pip install redis
ENV ACCESS_TOKEN=6172107145:AAG5Grx7OI38HOiq615cBadwCHiRk_UjC68
ENV HOST=redis-11196.c266.us-east-1-3.ec2.cloud.redislabs.com
ENV PASSWORD=9LYNHyce7b1dmQi9ygQuij0gBkGYRuYN
ENV REDISPORT=11196
CMD python chatbot.py


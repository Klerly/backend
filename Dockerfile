FROM python:3.9.12-slim-buster
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install procps -y
RUN apt-get install python3-pip python3-dev libpq-dev tk -y
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt
COPY /app /app/
EXPOSE 9000 8080 80
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["sh","/entrypoint.sh"]

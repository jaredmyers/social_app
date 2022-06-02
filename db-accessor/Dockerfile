FROM python:latest
WORKDIR /code
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt
ADD ./code/ .
CMD ["python3", "rpc_subscriber.py"]

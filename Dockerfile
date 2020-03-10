FROM python:3

RUN pip install mysql-connector-python

WORKDIR /server/

EXPOSE 5764

CMD ["python", "/server/server.py"]
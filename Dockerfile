FROM python:3

RUN pip install mysql-connector-python
RUN pip install scipy
RUN pip install numpy

WORKDIR /server/

EXPOSE 5764

CMD ["python", "/server/server.py"]
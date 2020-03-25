FROM python:3.8-alpine

RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh

RUN pip install mysql-connector-python
RUN pip install scipy
RUN pip install numpy
RUN pip install GitPython

WORKDIR /server/

EXPOSE 5764

CMD ["python", "/server/server.py"]
FROM python:3

RUN apt-get install -y git

RUN python -m pip install mysql-connector-python
RUN python -m pip install scipy
RUN python -m pip install numpy
RUN python -m pip install GitPython

WORKDIR /server/

EXPOSE 5764

CMD ["python", "/server/server.py"]
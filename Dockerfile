FROM python:3

WORKDIR /server/

RUN python -m pip install scipy
RUN python -m pip install numpy
RUN python -m pip install GitPython

EXPOSE 80

CMD ["python", "/server/server.py"]
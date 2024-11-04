FROM python:3-alpine

WORKDIR /opt/flex_proxy

COPY flex_proxy.py flex_proxy.py

EXPOSE 4996

CMD ["python", "./flex_proxy.py"]

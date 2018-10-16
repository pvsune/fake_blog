FROM python:3.7-slim

ENV HOST=0.0.0.0
ENV PORT=8080

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

COPY . /fake_blog
WORKDIR /fake_blog

EXPOSE $PORT
CMD python blog.py

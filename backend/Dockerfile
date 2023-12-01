FROM python:3.11

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt --no-cache-dir

COPY taxi/. .

CMD ["gunicorn", "--bind", "0.0.0.0:9000", "taxi.wsgi"]
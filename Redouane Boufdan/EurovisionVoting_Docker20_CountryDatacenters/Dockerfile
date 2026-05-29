FROM python:3.12-slim

WORKDIR /app
COPY . /app

ENV PYTHONUNBUFFERED=1
EXPOSE 8501

CMD ["python", "central_aggregator.py"]

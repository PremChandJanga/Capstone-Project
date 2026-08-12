FROM python:3.11-slim

WORKDIR /app

COPY task6/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY task1 ./task1
COPY task2 ./task2
COPY task3 ./task3
COPY task4 ./task4
COPY task5 ./task5

RUN python task1/ingest.py

EXPOSE 7860

CMD ["uvicorn", "task5.app:app", "--host", "0.0.0.0", "--port", "7860"]
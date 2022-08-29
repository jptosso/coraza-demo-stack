FROM python:latest
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY logger.py /app/logger.py
COPY entrypoint.sh /app/entrypoint.sh
ENTRYPOINT [ "/app/entrypoint.sh"]
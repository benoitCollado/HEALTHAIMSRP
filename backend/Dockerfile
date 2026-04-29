FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY migrations/ migrations/
COPY alembic.ini .
COPY pytest.ini .
COPY .coveragerc .
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]

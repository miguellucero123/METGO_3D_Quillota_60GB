FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app/

ENV METGO_API_PORT=8080
ENV METGO_API_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "backend/05_APIs_Externas/api_rest/app.py"]

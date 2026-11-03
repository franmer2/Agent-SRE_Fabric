FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app app

COPY services/fabric-admin-mcp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/fabric-admin-mcp/server.py .
COPY src/fabric_sre/__init__.py src/fabric_sre/capacity_metrics.py ./fabric_sre/

USER app
EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]

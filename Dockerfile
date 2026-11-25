FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY aruba_client.py server.py ./

RUN useradd -m appuser
USER appuser

ENV MCP_TRANSPORT=streamable-http \
    MCP_HTTP_HOST=0.0.0.0 \
    MCP_HTTP_PORT=8830

EXPOSE 8830

# A TCP connect is enough: the endpoint itself requires the bearer token.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import os,socket; socket.create_connection(('127.0.0.1', int(os.environ['MCP_HTTP_PORT'])), 3)"]

CMD ["python", "server.py"]

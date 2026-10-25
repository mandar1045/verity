# One image, whole product: UI build -> data generation -> training -> API that also serves the UI.
# Models are trained at build time with fixed seeds, so no model files are committed.

FROM node:20-alpine AS web
WORKDIR /app
COPY contracts/types.ts contracts/types.ts
COPY frontend/package.json frontend/package-lock.json frontend/
RUN cd frontend && npm ci --no-audit --no-fund
COPY frontend frontend
RUN cd frontend && VITE_API_URL= npx vite build

FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MPLBACKEND=Agg
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY contracts contracts
COPY data/__init__.py data/
COPY data/generators data/generators
COPY data/seeds data/seeds
COPY ml ml
COPY backend backend
RUN python -m data.generators.gen_messages \
 && python -m data.generators.gen_transactions \
 && python -m ml.message.train \
 && python -m ml.transaction.train \
 && python -m ml.eval.evaluate
COPY --from=web /app/frontend/dist frontend/dist
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/api/v1/health')"
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]

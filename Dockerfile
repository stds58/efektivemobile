FROM python:3.11-slim AS builder

ARG WORKDIR=/opt/backend

WORKDIR $WORKDIR
RUN pip install uv
ENV PATH="$WORKDIR/.venv/bin:$PATH"

COPY pyproject.toml .
RUN uv sync


FROM python:3.11-slim

ARG WORKDIR=/opt/backend
ARG USER=appuser

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR $WORKDIR

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder $WORKDIR/.venv $WORKDIR/.venv
ENV PATH="$WORKDIR/.venv/bin:$PATH"

RUN useradd -m appuser

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

ENV PATH="$WORKDIR/.venv/bin:$PATH"
USER appuser

CMD ["uvicorn", "app.main:app", "--workers", "4", "--host", "0.0.0.0"]
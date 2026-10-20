# Image backend CST (API Django et worker Celery).
# - Base épinglée par digest ; dépendances installées depuis requirements/production.lock.txt (versions et
#   empreintes figées) avec --require-hashes et uniquement des wheels.
# - Code propriété de root, en lecture seule pour cst ; seuls media/ et staticfiles/ lui appartiennent.
# - Pas de HEALTHCHECK ici : l'image sert aussi au worker Celery, chaque service déclare le sien.
FROM python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=180

WORKDIR /app

# Mêmes commandes qu'avant : uid et gid de cst inchangés pour les fichiers déjà présents dans les volumes.
RUN groupadd --system cst \
    && useradd --system --gid cst --create-home cst

COPY requirements ./requirements

RUN python -m pip install --no-cache-dir --retries 10 \
      --require-hashes --only-binary=:all: \
      -r requirements/production.lock.txt

COPY . .

RUN mkdir -p /app/media /app/staticfiles \
    && chown cst:cst /app/media /app/staticfiles

USER cst

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]

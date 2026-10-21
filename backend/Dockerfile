# Image backend CST (API Django et worker Celery).
# - Base Alpine, celle de SEME : aucune vulnérabilité HIGH ou CRITICAL, contrairement aux variantes Debian slim
#   (util-linux, perl, sqlite, zlib sans correctif). Épinglée par digest ; la rafraîchir délibérément, puis rescanner.
# - Dépendances installées depuis requirements/production.lock.txt (versions et empreintes figées) avec
#   --require-hashes et uniquement des wheels (musllinux) ; pip retiré ensuite.
# - Code propriété de root, en lecture seule pour cst ; seuls media/ et staticfiles/ lui appartiennent.
# - Pas de HEALTHCHECK ici : l'image sert aussi au worker Celery, chaque service déclare le sien.
ARG PYTHON_IMAGE=python:3.12-alpine@sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4

# Mêmes droits quel que soit le contexte de build (instantané de la CI aux répertoires en 0700, copie Windows aux
# fichiers en 0666) : répertoires 0755, fichiers 0644, 0755 s'ils sont exécutables. Seule cette étape paie le chmod.
FROM ${PYTHON_IMAGE} AS code
COPY . /code
RUN chmod -R u=rwX,go=rX /code

FROM ${PYTHON_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=180

WORKDIR /app

# uid et gid 999 comme dans l'ancienne image Debian : les fichiers déjà présents dans les volumes gardent leur
# propriétaire. Alpine donne le gid 999 à son groupe ping, inutile ici.
RUN delgroup ping \
    && addgroup -S -g 999 cst \
    && adduser -S -D -u 999 -G cst -h /home/cst -s /bin/sh cst

COPY --from=code /code/requirements ./requirements

RUN python -m pip install --no-cache-dir --retries 10 \
      --require-hashes --only-binary=:all: \
      -r requirements/production.lock.txt \
    && rm -rf /usr/local/lib/python3.12/site-packages/pip* /usr/local/bin/pip*

COPY --from=code /code/ /app/

# Le build échoue si cst (ni root ni membre de son groupe) ne pouvait pas lire son code ou pouvait le modifier :
# chaque répertoire o+rx, chaque fichier o+r, rien d'inscriptible par le groupe ou les autres, hors des deux volumes.
RUN mkdir -p /app/media /app/staticfiles \
    && chown cst:cst /app/media /app/staticfiles \
    && bad=$(find /app \( -path /app/media -o -path /app/staticfiles -o -type l \) -prune -o \
             \( -type d ! -perm -005 -o -type f ! -perm -004 -o -perm -020 -o -perm -002 \) -print | head -5) \
    && if [ -n "$bad" ]; then echo "Droits du code refusés pour cst : $bad" >&2; exit 1; fi

USER cst

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]

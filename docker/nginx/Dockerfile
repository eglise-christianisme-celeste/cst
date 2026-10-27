# Gateway applicatif CST / CSMO.
# Il ne contient ni le frontend ni le backend : il route uniquement les flux.
# nginx 1.30 (branche stable), épinglé par digest : la rafraîchir délibérément, puis rescanner.
FROM nginx:1.30-alpine@sha256:970364228b1e4f932abc22d321932816782cca8a20b85a77552a7cfe9acfb3b5

# Modules dynamiques livrés avec l'image mais jamais chargés ici (aucun load_module) : retirés hors réseau avec
# leurs dépendances (gd, libx11, fontconfig, libexpat, libxslt, geoip...). curl aussi, avec libcurl et brotli-libs
# (failles HIGH d'octobre 2026) : rien ne s'en sert, la sonde de santé utilise wget de busybox.
# Sans root : le processus maître tourne comme les workers (utilisateur nginx, port 8080), pid et fichiers
# temporaires dans /tmp. Les droits de lecture sur media et static ne changent pas (les workers étaient déjà nginx).
RUN apk del --no-network \
       nginx-module-image-filter nginx-module-xslt nginx-module-geoip nginx-module-njs nginx-module-acme curl \
    && sed -i -e '/^user /d' -e 's|^pid .*|pid /tmp/nginx.pid;|' /etc/nginx/nginx.conf \
    && printf '%s\n' 'client_body_temp_path /tmp/client_temp;' 'proxy_temp_path /tmp/proxy_temp;' \
       'fastcgi_temp_path /tmp/fastcgi_temp;' 'uwsgi_temp_path /tmp/uwsgi_temp;' 'scgi_temp_path /tmp/scgi_temp;' \
       > /etc/nginx/conf.d/00-unprivileged.conf

# Lisibles par nginx, modifiables par root seul, quel que soit le contexte de build.
COPY --chmod=0644 default.conf /etc/nginx/conf.d/default.conf
COPY --chmod=0644 errors/maintenance.html /usr/share/nginx/html/maintenance.html
COPY --chmod=0644 errors/system-error.html /usr/share/nginx/html/system-error.html

USER nginx

EXPOSE 8080

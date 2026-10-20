# Gateway applicatif CST / CSMO.
# Il ne contient ni le frontend ni le backend : il route uniquement les flux.
# Même image que le proxy partagé ecc-shield, épinglée par digest.
FROM nginx:1.28.3-alpine@sha256:a8b39bd9cf0f83869a2162827a0caf6137ddf759d50a171451b335cecc87d236

# Sans root : le processus maître tourne comme les workers (utilisateur nginx, port 8080), pid et fichiers
# temporaires dans /tmp. Les droits de lecture sur media et static ne changent pas (les workers étaient déjà nginx).
RUN sed -i -e '/^user /d' -e 's|^pid .*|pid /tmp/nginx.pid;|' /etc/nginx/nginx.conf \
    && printf '%s\n' 'client_body_temp_path /tmp/client_temp;' 'proxy_temp_path /tmp/proxy_temp;' \
       'fastcgi_temp_path /tmp/fastcgi_temp;' 'uwsgi_temp_path /tmp/uwsgi_temp;' 'scgi_temp_path /tmp/scgi_temp;' \
       > /etc/nginx/conf.d/00-unprivileged.conf

COPY default.conf /etc/nginx/conf.d/default.conf
COPY errors/maintenance.html /usr/share/nginx/html/maintenance.html
COPY errors/system-error.html /usr/share/nginx/html/system-error.html

USER nginx

EXPOSE 8080

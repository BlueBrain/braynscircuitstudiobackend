ARG BCSB_IMAGE=bbpgitlab.epfl.ch:5050/viz/brayns/braynscircuitstudiobackend

FROM $BCSB_IMAGE as backend

WORKDIR /usr/src/braynscircuitstudiobackend/

RUN python manage.py collectstatic --no-input



FROM nginx:stable-alpine

ARG NGINX_HTML_ROOT=/usr/share/nginx/html

RUN test -e /var/run || ln -s /run /var/run

ADD ./nginx/default.conf /etc/nginx/conf.d

COPY --from=backend /usr/src/braynscircuitstudiobackend/staticfiles/ $NGINX_HTML_ROOT/static/

RUN chown -R nginx:nginx $NGINX_HTML_ROOT && chmod -R 755 $NGINX_HTML_ROOT && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d

RUN touch /var/run/nginx.pid

RUN chown -R nginx:nginx /var/run/nginx.pid

USER nginx

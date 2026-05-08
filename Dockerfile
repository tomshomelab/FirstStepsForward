FROM nginx:alpine

COPY default.conf /etc/nginx/conf.d/default.conf

COPY public/    /usr/share/nginx/html/
COPY assets/    /usr/share/nginx/html/assets/

EXPOSE 80

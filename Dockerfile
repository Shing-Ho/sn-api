FROM python:3.7

RUN apt-get -y update
RUN apt-get -y install apt-utils supervisor nginx

RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app
RUN pip3 install --requirement requirements.txt

COPY . /app/
COPY ./conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY ./conf/api-nginx.conf /etc/nginx/sites-enabled/default

EXPOSE 80

RUN ln -sf /dev/stdout /var/log/supervisor/access.log
RUN ln -sf /dev/stderr /var/log/supervisor/error.log

# Set certificate permissions
RUN chmod 0600 ./app/secrets/*.pem
RUN chmod 0600 ./app/secrets/prod/*.pem

# for production
CMD bash -c "exec /usr/bin/supervisord"
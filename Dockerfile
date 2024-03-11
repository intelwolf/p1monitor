FROM debian:bookworm-slim
#FROM debian:bullseye-slim

# Set timezone
#RUN ln -fs /usr/share/zoneinfo/Europe/Amsterdam /etc/localtime && dpkg-reconfigure -f noninteractive tzdata
ENV TZ="Europe/Amsterdam"

# Install packages
RUN apt-get update && apt-get upgrade -y && apt-get install -y python3-venv python3-cryptography python3-pip python3-bcrypt python3-falcon nginx-full php-fpm sqlite3 php-sqlite3 python3-cairo python3-apt vim cron sudo logrotate curl iputils-ping iproute2 libffi-dev socat python3-nacl && apt-get clean

RUN addgroup -gid 1002 gpio && addgroup -gid 1001 p1mon && adduser --gid 1001 --disabled-password --gecos "P1Mon" p1mon && usermod -aG p1mon www-data && usermod -aG www-data,gpio,dialout p1mon

# Setup sudo without password for p1mon and www-data
RUN echo >>/etc/sudoers "p1mon ALL=(ALL) NOPASSWD: ALL" && echo >>/etc/sudoers "www-data ALL=(p1mon) NOPASSWD: /p1mon/scripts/*"

# Install Python packages required
#RUN pip3 install pythoncrc gunicorn certifi cffi chardet colorzero dropbox falcon future gpiozero idna iso8601 paho-mqtt pigpio psutil pycparser pycrypto pyserial python-crontab python-dateutil pytz PyYAML requests RPi.GPIO setuptools spidev urllib3 xlsxwriter
RUN pip3 install --break-system-packages pythoncrc gunicorn certifi cffi chardet colorzero dropbox future idna iso8601 paho-mqtt pigpio psutil pycparser pycrypto pyserial python-crontab python-dateutil pytz PyYAML requests rpi-lgpio RPi.GPIO setuptools spidev urllib3 xlsxwriter

# Copy original p1mon directory
COPY --chown=p1mon:p1mon p1mon/ /p1mon/

# Additional configurations
COPY --chown=p1mon:p1mon addons /
COPY  addonsbin /

HEALTHCHECK CMD curl -f http://127.0.0.1/nginx_status/ || exit 1

USER p1mon 

ENTRYPOINT ["/entrypoint.sh"]

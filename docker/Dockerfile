FROM centos:7

RUN yum -y install epel-release
RUN yum -y install nginx gcc supervisor net-tools vim less pwgen python-pip
RUN pip install --upgrade pip setuptools distribute
RUN pip install dumb-init

RUN yum -y install https://centos7.iuscommunity.org/ius-release.rpm
RUN yum -y install python36u python36u-devel python36u-pip
# RUN pip3.6 install --upgrade pip setuptools distribute

RUN mkdir -p /etc/nginx/ssl
WORKDIR /etc/nginx/ssl
RUN pwgen 32 1 > keypass
RUN openssl genrsa -out key.pem -passout file:keypass 4096
RUN openssl rsa -in key.pem -out server.key -passin file:keypass
RUN openssl req -x509 -key server.key -out server.pem -days 365 -passin file:keypass \
    -subj "/C=NL/ST=North Holland/L=Amsterdam/O=Giuseppe Chiesa/OU=SRE Department/CN=localhost"
RUN rm keypass

RUN ln -sf /dev/stdout /var/log/nginx/access.log
RUN ln -sf /dev/stderr /var/log/nginx/error.log

ENTRYPOINT ["/usr/bin/dumb-init", "--"]



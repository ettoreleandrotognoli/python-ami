FROM fedora AS base
FROM base as builder

ARG ASTERISK_VERSION=19.3.1

RUN dnf update -y \
        && dnf groupinstall -y "Development Tools" \
        && dnf install -y openssl-devel gcc gcc-c++ bzip2 libedit-devel uuid-devel libuuid-devel jansson-devel libxml2-devel sqlite-devel \
        && dnf clean all \
        && rm -rf /var/cache/yum

RUN git clone --depth 1 --branch ${ASTERISK_VERSION} --single-branch  https://github.com/asterisk/asterisk.git /usr/src/asterisk
WORKDIR /usr/src/asterisk
RUN ./configure
RUN make install
RUN make samples


#FROM builder as runtime
EXPOSE 5038
COPY ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
ENV AMI_USER="admin"
ENV AMI_SECRET="password"
CMD ["asterisk","-f","-v"]
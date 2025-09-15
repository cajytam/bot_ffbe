FROM alpine:latest

RUN apk update && \
    apk add --no-cache openrc \
    python3 \
    py3-pip \
    gcc \
    musl-dev \
    bash-completion \
    tor \
    nano

RUN echo 'alias py="python3"' >> /root/.bashrc

RUN pip3 install --break-system-packages stem \
    requests \
    requests[socks] \
    pysocks \
    pyyaml \
    pycryptodome

RUN rc-update add tor


WORKDIR /app/

ENV PYTHONPATH=/app
# USER tor

EXPOSE 9050

COPY torrc /etc/tor/torrc
CMD /usr/bin/tor -f /etc/tor/torrc

# CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "3000"]

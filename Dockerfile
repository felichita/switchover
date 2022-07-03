# syntax=docker/dockerfile:experimental
ARG REGISTRY_URL=$REGISTRY_URL
ARG CI_PROJECT_NAME=$CI_PROJECT_NAME
FROM $REGISTRY_URL/xnt/debian/buster:latest


ENV HOME=/app
ENV LANG en_US.utf8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN mkdir ${HOME}
WORKDIR ${HOME}

COPY . .

RUN curl -sS https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list && \
    apt update && \
    apt install -y kubectl python3.7-dev git python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 10 && \
    pip3 install --upgrade pip -U && \
    pip3 install -r /app/requirements.txt && \
    rm -rf /root/.cache 

ENTRYPOINT ["gunicorn"]
CMD ["-c", "/etc/app/gunicorn.conf.py", "wsgi"]

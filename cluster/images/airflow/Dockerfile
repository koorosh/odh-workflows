ARG airflow_ver=2.0.1
ARG python_ver=3.8

FROM apache/airflow:${airflow_ver}-python${python_ver}

# Pretend to be a super user to install extra dependencies
USER root

RUN apt-get update && \
    apt-get install -y \
    curl \
    vim \
    software-properties-common \
    ssh \
    net-tools \
    ca-certificates \
    jq \
    tar \
    unzip

EXPOSE 22
USER airflow
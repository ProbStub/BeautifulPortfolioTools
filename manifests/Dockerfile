# CI host image for Beautiful Portfolio Tools - using brew to keep setup tooling synced between macOS & Ci Linux image
# ubuntu because alpine continues to have old glibc with complicated upgrade path
# NOTE: CircleCI presubable does a "-v /var/run/docker.sock:/var/run/docker.sock" when requesting "setup_remote_docker"
#       for local runs the "-v..." option needs to be supplied to the "docker run" command for thid Dockerfile to work
# WARNING: All Kubernetes workload images are generic and in no way security harded or performance optimized!

# Docker -> kind -> Docker for pods
FROM ubuntu:latest

# Using ubuntu packages for system prerequisists only
RUN apt update
RUN apt install -y curl ruby git ca-certificates grep build-essential sudo lsb-release gnupg iputils-ping net-tools

# Fetch and install docker container engine
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg]\
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt update
ENV DEBIAN_FRONTEND=noninteractive
RUN apt install -y docker-ce docker-ce-cli containerd.io
RUN newgrp docker

# Adding linuxbrew user needed for brew installation
RUN adduser --disabled-password --shell /bin/bash --gecos "" linuxbrew
RUN echo 'linuxbrew ALL=(ALL) NOPASSWD:ALL' >>/etc/sudoers
USER linuxbrew
WORKDIR /home/linuxbrew
ENV PATH=/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:$PATH \
	SHELL=/bin/bash \
	USER=linuxbrew
RUN sudo usermod -aG docker linuxbrew && newgrp docker

# Installing homebrew aka linuxbrew including essential package updates/configuration
RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
RUN echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> /home/linuxbrew/.profile
RUN eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

# Insalling Kubernetes and ISTIO
RUN brew install kind kubectl helm
RUN curl -L https://istio.io/downloadIstio | sh -
RUN export ISTIO_HOME=$(ls|grep istio)
ENV PATH=$ISTIO_HOME/bin:$PATH
ENV CLUSTER_NAME=bpt-ci-cluster
ENV CLUSTER_CONTROL_PLANE=$CLUSTER_NAME"-control-plane"

# Installing Python & PySpark requirements
RUN brew install python3
# Do NOT "pip3 install pyspark" as it unsettles the JAVA environment for spark
# TODO: retrieve exact package list from requirements.txt through CI environment parameters
RUN pip3 install pandas pyarrow
RUN brew install apache-spark

# Install Postgres operator
RUN cd
RUN git clone https://github.com/zalando/postgres-operator.git

# Install MongoDB operator
RUN cd
RUN git clone https://github.com/mongodb/mongodb-kubernetes-operator.git


# TODO Complete production configuration and
# - Install Spark Operator (https://operatorhub.io/operator/spark-gcp)
# - Install Spinnaker Operator (https://operatorhub.io/operator/spinnaker-operator)
# - Install Kafka Operator (https://operatorhub.io/operator/strimzi-kafka-operator)
# - Retrieve exact package list from requirements.txt through CI environment parameters
# - Post-CI container engineering/hardening remove unnecessary accounts and tools, e.g. more, grep, etc.

# Run entrypoint script that depends on actual container id and network post image creation
RUN cd
RUN cd
COPY entrypoint.sh .
RUN sudo chown $(whoami) entrypoint.sh
RUN sudo chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
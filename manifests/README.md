# Environment Setup
If you do not have an existing environment to deploy to you should refer to the prepared [Dockerfile](Dockerfile).
This container creates a service mesh with MongoDB, Postgres and PySpark (3.2.0) using kind instead of minikube.
The environment is suitable for development or continues integration. However, all data and credentials
(e.g., database passwords) are lost when the container is restarted. The container is exposing the internal
databases and logs should display the session database password when you run:
```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock -p 27017:27017 -p 5432:5432
```
This is the easiest (by far not the safes!) way to get started with Beautiful Portfolio Tools.
You can access the container after it has successfully launched by typing the below into a commandline terminal:
```bash
docker exec -i -t bpt-ci /bin/bash
```
Additional ports (such as 20001, 3000, 443, 6443, 80 or 8081) may be exposed using the ```-p``` option.
You should allocate at least 15GB memory and 12 cpus/cores to Docker or else there won't much resources for Spark
execution pods to be created.

If you prefer to work in your local environment please consider the instructions below a rough guide.

## Prerequisite for local setup
This describes the general <b>local</b> environment setup (read: minikube)
assuming you have no tooling what-so-ever.
The steps may vary on your machine and are by no means complete.

1. Install [Docker](https://www.docker.com) - You may as well create DockerHub account, although not strictly required
2. Install [Homebrew](https://brew.sh) and check that ```.zprofile``` includes the brew shellenv:
```/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"```
3. Install Python (v3.9+): ```brew install python3```
4. Install minikube: ```brew install minikube```
5. Start minikube: ```minikube start``` - when planning for Istio add ```--cpu 6 --memory 6144```

## PySpark Kubernetes local deployment
1. Install PySpark using Homebrew (verify ```.zprofile``` in your home points to
correct Java/Python paths by comparing with output of ```which python3``` etc.):```brew install apache-spark```
2. Switch to minikube docker environment: ```eval $(minikube docker-env)```
3. Build spark Kubernetes Docker image, adapt as necessary (cd to libexec directory
   of your apache-spark installation): ```docker-image-tool.sh -b platform=linux/amd64 -n -t spark -p \
kubernetes/dockerfiles/spark/bindings/python/Dockerfile build```
4. Note the image tag at the end of the previous command and adjust the ``ìmage:`` parameter in
   ```spark_minikube.yaml```. It should be ```spark-py:spark``` if nothing was changed in the command above
5. Run ```kubctl cluster-info``` and record links and ports in your ```.enf``` file

## Postgres Kubernetes local deployment
2.Get the [Zalando Postgres Kubernetes operator](https://postgres-operator.readthedocs.io/en/latest/quickstart/)
installed
4. Obtain Postgres host & port and insert into your ```.env``` file (keep the terminal open on macOS):
```minikube service acid-minimal-cluster --url | sed 's,.*/,,' &```
5. Obtain Postgres password & password for ```.env``` (the <b>username postgres</b> is fixed
remove, if any, trailing special character:
```kubectl get secret postgres.acid-minimal-cluster.credentials -o 'jsonpath={.data.password}' | base64 -d```

## MongoDB remote or Kubernetes local deployment
1. Create accounts at Google Cloud Platform and MongoDB to install a hosted MongoDB Atlas instance (for free) and
record the hostname, port, username & password in your ```.env``` file -
2. OR: Optionally use the [MongoDB Kubernetes operator](https://github.com/mongodb/mongodb-kubernetes-operator.git)

## (Optional) Istio system orchestation
Before you start ensure that
1. Download and unpack (for macOS and Linux): ```curl -L https://istio.io/downloadIstio | sh -```
2. Move files to an appropriate directory and executables to your path. Either
   a) temporary by running ```export PATH=$PATH:/path/to/istio/bin``` or
   b) permanently in ````~/.zprofile```` (exit and restart your shall, or run ```source ~/.zprofile```)
3. Install Istio on the minikube cluster: ```istioctl install```
4. Enable a designated namespace for Istio to manage: ````kubectl label namespace default istio-injection=enabled````

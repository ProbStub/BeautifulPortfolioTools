# Environment Setup
If you do not have an existing environment to deploy to below are a few critical
steps to take before BPT code will run. This may be refactored into an
automated environment setup as part of the CircleCI CI/CD pipeline.
However, for the moment you need to perform these steps manually.

> WARNING: Setup instructions may not be complete until CI/CD pipeline is
> fully migrated to CircleCI


## Prerequisite setup
This describes the general <b>local</b> environment setup (read: minikube)
assuming you have no tooling what-so-ever.
The steps may vary on your machine and are by no means complete.

1. Install [Docker](https://www.docker.com) - You may as well create DockerHub account, although not strictly required
2. Install [Homebrew](https://brew.sh) and check that ```.zprofile``` includes the brew shellenv:
```/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"```
3. Install Python: ```brew install python3```
4. Install minikube: ```brew install minikube```
5. Start minikube: ```minikube start```

## PySpark Kubernetes deployment
1. Install PySpark using Homebrew (verify ```.zprofile``` in your home points to
correct Java/Python paths by comparing with output of ```which python3``` etc.):```brew install apache-spark```
2. Switch to minikube docker environment: ```eval $(minikube docker-env)```
3. Build spark Kubernetes Docker image, adapt as necessary (cd to libexec directory
   of your apache-spark installation): ```docker-image-tool.sh -b platform=linux/amd64 -n -t sparkk8x86 -p \
kubernetes/dockerfiles/spark/bindings/python/Dockerfile build```
4. Note the image tage at the end of the previous command and adjust the ``ìmage:`` parameter in
   ```spark_minikube.yaml```. It should be ```spark-py:spark``` if nothing was changed in the command above
5. Change back to the manifest folder (this directory) and initiate the cluster by running:
```kubectl apply -f spark_minikube.yaml```
6. Verify that the spark cluster is ready: ```kubectl get pod -l app=BeautifulPortfolioTools -n spark```

> NOTE: While refactoring the build pipeline from local minikube to CircleCi/GKE the YAML may not
> produce any useful environment as namespaces, registry location, networking and storage needs refinement

## Postgres Kubernetes deployment
2.Get the [Zalando Postgres Kubernetes operator](https://postgres-operator.readthedocs.io/en/latest/quickstart/)
installed
4. Obtain Postgres host & port and insert into your ```.env``` file (keep the terminal open on macOS):
```minikube service acid-minimal-cluster --url | sed 's,.*/,,' &```
5. Obtain Postgres password & password for ```.env``` (the <b>username postgres</b> is fixed
remove, if any, trailing special character:
```kubectl get secret postgres.acid-minimal-cluster.credentials -o 'jsonpath={.data.password}' | base64 -d```
6. Create accounts at Google Cloud Platform and MongoDB to install a hosted MongoDB Atlas instance (for free) and
record the hostname, port, username & password in your ```.env``` file -
Optionally use the [MongoDB Kubernetes operator](https://www.mongodb.com/try/download/community-kubernetes-operator)
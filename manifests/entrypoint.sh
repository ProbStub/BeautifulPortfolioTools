#!/bin/bash
# NOTE
# CircleCI/docker-in-docker sections are marked specifically.
# Assuming local environment preparation, other commands can be executed locally against defined K8 context.
#
# WARNING
# This is designed for development and integration testing only. Before production use consider the following:
# - Review all container images software/package version, user account and network settings in containers
# - Set app/version labels on all pods/services & workloads for ISTIO and to conform with your environment policies
# - Define persistent volumes to match your environment policies
# - Remove unnecessary accounts and tools, e.g. more, grep, etc.
# - Enable Spinnaker deployment support (https://github.com/armory/spinnaker-operator)
# - Consider Kafka for model serving (https://operatorhub.io/operator/strimzi-kafka-operator)

# START CircleCI/docker-in-docker specific
sudo chgrp docker /var/run/docker.sock
sudo chmod 775 /var/run/docker.sock

# Cleanup residual cluster from previous run, if any
kind delete clusters $(kind get clusters)

# Create kind cluster and establish networking connectivity for docker-in-docker setup
kind create cluster --name $CLUSTER_NAME
export MASTER_IP=$(docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' \
      $CLUSTER_CONTROL_PLANE)
sed -i "s/^    server:.*/    server: https:\/\/$MASTER_IP:6443/" $HOME/.kube/config
export MASTER_NET=$(docker inspect --format='{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}' \
           $CLUSTER_CONTROL_PLANE)
docker network connect $MASTER_NET $HOSTNAME
# END CircleCI/docker-in-docker specific

# ISTIO main and service add-on components startup
$(ls|grep istio)/bin/istioctl install -y
kubectl label namespace default istio-injection=enabled
kubectl apply -f $PWD/$(ls|grep istio)/samples/addons
echo "Waiting for ISTIO services:"
echo -n "Starting prometheus [";
until kubectl get pods -n istio-system -l app=prometheus -o=jsonpath='{range .items[*]}{@.status.phase}' | grep -m1 "Running" &> /dev/null;
do
  echo -n "*";
  sleep 1;
  done;
echo "] DONE!"
echo -n "Starting grafana [";
until kubectl get pods -n istio-system -l app=grafana -o=jsonpath='{range .items[*]}{@.status.phase}' | grep -m1 "Running" &> /dev/null;
do
  echo -n "*";
  sleep 1;
  done;
echo "] DONE!"
echo -n "Starting kiali [";
until kubectl get pods -n istio-system -l app=kiali -o=jsonpath='{range .items[*]}{@.status.phase}' | grep -m1 "Running" &> /dev/null;
do
  echo -n "*";
  sleep 1;
  done;
echo "] DONE!"
# Adding the kube-system metrics server configuration
cd

#sed -i -e 's/- --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname/- --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname\
#          - --kubelet-insecure-tls/' metrics-server/manifests/base/deployment.yaml

sed -i -e 's/kubelet-use-node-status-port/kubelet-insecure-tls/' metrics-server/manifests/base/deployment.yaml
#sed -i -e 's/periodSeconds: 10/periodSeconds: 30/' metrics-server/manifests/base/deployment.yaml
kubectl apply -k metrics-server/manifests/release/



# Postgres operator configuration
cd postgres-operator/
sed -i -e 's/cluster_labels: application:spilo/cluster_labels: application:spilo, app:postgres, version:v1/' manifests/configmap.yaml
## Launching postgres operator and cluster instance
kubectl create -f manifests/configmap.yaml
kubectl create -f manifests/operator-service-account-rbac.yaml
kubectl create -f manifests/postgres-operator.yaml
kubectl apply -f ui/manifests/
echo "Waiting for Postgres operator:"
echo -n "Starting operator [";
until kubectl get pods -n default -l name=postgres-operator -o=jsonpath='{range .items[*]}{@.status.phase}' | grep -m1 "Running" &> /dev/null;
do
  echo -n "*";
  sleep 1;
  done;
echo "] DONE!"
kubectl create -f manifests/minimal-postgres-manifest.yaml
echo "Waiting for Postgres cluster:"
echo -n "Starting postgres cluster [";
until kubectl get pods -n default -l app=postgres -o=jsonpath='{range .items[*]}{@.status.phase}' | grep -m1 "Running" &> /dev/null;
do
  echo -n "*";
  sleep 1;
  done;
echo "] DONE!"
export PGPORT=$(kubectl get service acid-minimal-cluster --output='jsonpath={.spec.ports[0].port}')
kubectl port-forward statefulset/acid-minimal-cluster --address=0.0.0.0 $PGPORT&
export PGHOST=0.0.0.0
export PGUSER=$(kubectl get secret postgres.acid-minimal-cluster.credentials.postgresql.acid.zalan.do -o 'jsonpath={.data.username}' | base64 -d)
export PGPWD=$(kubectl get secret postgres.acid-minimal-cluster.credentials.postgresql.acid.zalan.do -o 'jsonpath={.data.password}' | base64 -d)
export PGSSLMODE=require
cd

# MongoDB operator configuration
cd
cd mongodb-kubernetes-operator/
sed -i -e 's/^  labels:/  labels:\
    app: mongodb-operator\
    version: v1/' config/manager/manager.yaml
sed -i -e 's/^      labels:/      labels:\
        app: mongodb-operator\
        version: v1/' config/manager/manager.yaml
sed -i -e 's/  name: example-mongodb/  name: mongodb\
  labels:\
    app: mongodb/' config/samples/mongodb.com_v1_mongodbcommunity_cr.yaml
# Assign same PW as for postgres
sed -i -e 's/<your-password-here>/'$PGPWD'/' config/samples/mongodb.com_v1_mongodbcommunity_cr.yaml
# Launching MongoDB operator and cluster instance
kubectl apply -f config/crd/bases/mongodbcommunity.mongodb.com_mongodbcommunity.yaml
kubectl apply -k config/rbac/ --namespace default
kubectl create -f config/manager/manager.yaml --namespace default
# Waiting for mongodb operator
echo -n "Starting mongodb operator [";
until kubectl get pods -n default -l app=mongodb-operator -o=jsonpath='{range .items[*]}{@.status.phase}' | grep -m1 "Running" &> /dev/null;
do
  echo -n "*";
  sleep 1;
  done;
echo "] DONE!"
kubectl apply -f config/samples/mongodb.com_v1_mongodbcommunity_cr.yaml --namespace default
# Waiting for mongodb cluster instance (wait for 3 X "Running", 3 members defined in mongodb.com_v1_mongodbcommunity_cr.yaml)
echo -n "Starting mongodb cluster [";
until kubectl get pods -n default -l app=mongodb-svc -o=jsonpath='{range .items[*]}{@.status.phase}' | grep -m1 "RunningRunningRunning" &> /dev/null;
do
  echo -n "*";
  sleep 1;
  done;
echo "] DONE!"
# Waiting for mongodb secrets availability to extract port data
echo -n "Waiting for mongodb secrets availability (ignore errors for a few minutes. MongoDB needs quite some time...)";
until kubectl get secrets mongodb-admin-my-user -o=jsonpath='{.data.connectionString\.standard}'|base64 -d | grep "^mongodb" &> /dev/null;
do
  echo -n "";
  sleep 1;
  done;
echo "DONE!"
export MGUSR=$(kubectl get secrets mongodb-admin-my-user -o=jsonpath='{.data.username}'|base64 -d)
export MGPWD=$(kubectl get secrets mongodb-admin-my-user -o=jsonpath='{.data.password}'|base64 -d)
export MGPORT=$(kubectl get secrets mongodb-admin-my-user -o=jsonpath='{.data.connectionString\.standard}'|base64 -d|grep -o ':[0-9]*\/admin' | grep -o '[0-9]*')
kubectl port-forward statefulset/mongodb --address=0.0.0.0 $MGPORT&
export CONSTD=$(kubectl get secrets mongodb-admin-my-user -o=jsonpath='{.data.connectionString\.standard}'|base64 -d)
export CONSRV=$(kubectl get secrets mongodb-admin-my-user -o=jsonpath='{.data.connectionString\.standardSrv}'|base64 -d)
cd

# Spark kubernetes operator configuration
export LATEST_SPARK=$(ls -t ".linuxbrew/Cellar/apache-spark/" | head -n 1)
cd .linuxbrew/Cellar/apache-spark/$LATEST_SPARK/libexec
docker-image-tool.sh -b platform=linux/amd64 -n -t spark -p kubernetes/dockerfiles/spark/bindings/python/Dockerfile build
cd
kind load docker-image spark-py:spark --name $CLUSTER_NAME
sed -i -e 's/^  labels:/  labels:\
    app: sparkoperator\
    version: 3.1.1/' spark-on-k8s-operator/manifest/spark-operator-install/spark-operator.yaml
sed -i -e 's/^      labels:/      labels:\
        app: sparkoperator\
        version: 3.1.1/' spark-on-k8s-operator/manifest/spark-operator-install/spark-operator.yaml
# Launching Spark operator instance
kubectl apply -f spark-on-k8s-operator/manifest/crds/
kubectl apply -f spark-on-k8s-operator/manifest/spark-application-rbac/
kubectl apply -f spark-on-k8s-operator/manifest/spark-operator-install/

# 3.1.1 operator run with spark 3.2.0 image:
#sed -i -e 's/gcr.io\/spark-operator\/spark-py:v3.1.1/spark-py:spark/' spark-on-k8s-operator/examples/spark-py-pi.yaml
#sed -i -e 's/3.1.1/3.2.0/' spark-on-k8s-operator/examples/spark-py-pi.yaml
#sed -i -e 's/imagePullPolicy: Always/imagePullPolicy: Never/' spark-on-k8s-operator/examples/spark-py-pi.yaml
#kubectl apply -f spark-on-k8s-operator/examples/spark-py-pi.yaml
#kubectl get sparkapplications pyspark-pi -o=yaml

# Client run:
#kubectl create serviceaccount spark
#kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default
#spark-submit --master k8s://https://172.18.0.2:6443 \
#--deploy-mode cluster \
#--name spark-pi \
#--class org.apache.spark.examples.SparkPi \
#--conf spark.executor.instances=2 \
#--conf spark.kubernetes.container.image=spark-py:spark  \
#--conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
#local:///opt/spark/examples/jars/spark-examples_2.12-3.2.0.jar 1000

# START CircleCI/docker-in-docker specific
# TODO: Operator UI port-forwards
kubectl port-forward svc/kiali --address=0.0.0.0 20001 -n istio-system &
kubectl port-forward svc/grafana --address=0.0.0.0 3000 -n istio-system &
kubectl port-forward svc/istio-ingressgateway --address=0.0.0.0 80 -n istio-system &
kubectl port-forward svc/istio-ingressgateway --address=0.0.0.0 443 -n istio-system &
kubectl port-forward svc/postgres-operator-ui --address=0.0.0.0 8081:80 &
# END CircleCI/docker-in-Docker specific
sleep 3
echo "#####################################################################################################################"
echo "Session database password (postgres and mongodb) is: $PGPWD"
echo "Note: The container is ephemeral. Passwords WILL CHANGE after restart!"
echo "WARNING: Data will be ERASED upon restart. Data is NOT PERSISTED in the integration environment!"
echo "#####################################################################################################################"
bash
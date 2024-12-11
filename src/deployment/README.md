# Deployment

This module executes Ansible Playbooks to build our frontend and api-service and build a Kubernetes cluster to run our app via GCP.

## Build Container

To build the container, run:

```bash
sh docker-shell.sh
```

## Workflow to Build and Deploy the App

1. If needed, build the required containers (frontend and api-serivce) and push to GCR.

```bash
ansible-playbook deploy-docker-images.yml -i inventory.yml
```


2. Create and deploy a Kubernetes cluster:

```bash
ansible-playbook deploy-k8s-cluster.yml -i inventory.yml --extra-vars cluster_state=present
```

3. Copy the `nginx_ingress_ip` output from the previous step and go to `http://<YOUR INGRESS IP>.sslip.io`. The app should be deployed with both the frontend and api-service active (along with access to the necessary GCP resources).

4. To delete the cluster:
```bash
ansible-playbook deploy-k8s-cluster.yml -i inventory.yml --extra-vars cluster_state=absent
```

## Workflow to Update the App
1. Once the Kubernetes clusters have been built, changes to the frontend or api-service can easily be changed with
```bash
ansible-playbook deploy-k8s-cluster.yml -i inventory.yml --extra-vars cluster_state=absent
```bash
sh deploy-k8s-update.sh
```
Please note that this mimics the exact behavior if you were to use the Github Action to update the app. This is further explained on the root README. Lastly, using this workflow assumes that you already have a cluster (with the correct name) running. If you do not, this playbook will fail after the frontend/api-service is pushed to GCR.

## Manual Workflow to Build and Deploy the App
While not recommended (as the workflow above will automatically build the cluster and deploy the app), you can manually start a VM and deploy the app. To briefly go over this method:

**Make sure to start the ``deployment`` container via `docker-shell.sh`.**

1.  Build and Push Docker Containers to GCR
```bash
ansible-playbook deploy-docker-images.yml -i inventory.yml
```

2. Create a Compute Instance in GCP
```bash
ansible-playbook deploy-create-instance.yml -i inventory.yml --extra-vars cluster_state=present
```

3. Install and setup the required components for deployment.
```bash
ansible-playbook deploy-provision-instance.yml -i inventory.yml
```

4. Setup Docker Containers in the Compute Instance
```bash
ansible-playbook deploy-setup-containers.yml -i inventory.yml
```

5. Setup Webserver on the Compute Instance
```bash
ansible-playbook deploy-setup-webserver.yml -i inventory.yml
```

6. Once satisfied, delete the Compute Instance
```bash
ansible-playbook deploy-create-instance.yml -i inventory.yml --extra-vars cluster_state=absent
```

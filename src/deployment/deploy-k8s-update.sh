ansible-playbook deploy-docker-images.yml -i inventory-prod.yml
ansible-playbook update-k8s-cluster.yml -i inventory-prod.yml
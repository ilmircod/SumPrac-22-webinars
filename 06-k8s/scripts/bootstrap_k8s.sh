#!/bin/sh

# Update and install utils
echo "Updating linux"
echo "..."
sudo apt update && sudo apt upgrade -y
echo "Success"
echo ""
echo "Installing curl, nano"
echo "..."
sudo apt install curl nano -y
echo "Success"
echo ""

# Install awscli
echo "Installing awscli"
echo "..."
sudo pip install awscli --upgrade
echo "----------------------------------------"
echo "awscli installed success"
echo "awscli version is --- $(aws --version)"
echo ""

# Install eksctl
echo "Installing eksctl"
echo "..."
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
echo "----------------------------------------"
echo "eksctl installed success"
echo "eksctl version is --- $(eksctl version)"
echo ""

# Install kubectl
echo "Installing kubectl"
echo "..."
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv ./kubectl /usr/local/bin
echo "----------------------------------------"
echo "kubectl installed success"
echo "kubectl version is --- $(kubectl version)"
echo ""

# Install Helm Charts
echo "Installing Helm Charts"
echo "..."
curl -LO -s https://get.helm.sh/helm-v3.7.0-linux-amd64.tar.gz
tar -xf helm-v3.7.0-linux-amd64.tar.gz
cd linux-amd64/
sudo mv helm /bin/
cd ..
rm -rf linux-amd64/ helm-v3.7.0-linux-amd64.tar.gz
echo "----------------------------------------"
echo "Helm Charts installed success"
echo "Helm Charts version is --- $(kubectl version)"
helm version
echo ""

# Install kubectx, kubens
echo "Removing old version of kubectx"
echo "..."
sudo rm -rf /opt/kubectx
sudo unlink /usr/local/bin/kubectx
sudo unlink /usr/local/bin/kubens
echo "----------------------------------------"
echo "Successfull"
echo ""
echo "Installing kubectx, kubens"
echo "..."
sudo git clone https://github.com/ahmetb/kubectx /opt/kubectx
sudo ln -s /opt/kubectx/kubectx /usr/local/bin/kubectx
sudo ln -s /opt/kubectx/kubens /usr/local/bin/kubens
echo "----------------------------------------"
echo "Successfull"
echo "kubectx installed success"
echo "kubectx result is --- $(kubectx)"
echo "kubens installed success"
echo "kubens result is --- $(kubens)"
echo ""
#!/bin/bash

# Privacy-Focused Services Deployment Script for K3s with Longhorn and NFS
# This script deploys all privacy-focused services mentioned in the XDA article

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    print_success "kubectl is available"
}

# Function to check if K3s cluster is accessible
check_cluster() {
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to K3s cluster"
        exit 1
    fi
    print_success "Connected to K3s cluster"
}

# Function to check storage classes
check_storage() {
    print_status "Checking storage classes..."
    
    if ! kubectl get storageclass longhorn &> /dev/null; then
        print_warning "Longhorn storage class not found. Please ensure Longhorn is installed."
        print_status "To install Longhorn, run:"
        echo "kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.8.1/deploy/longhorn.yaml"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "Longhorn storage class found"
    fi
    
    if ! kubectl get storageclass nfs-client &> /dev/null; then
        print_warning "NFS storage class not found. Please ensure NFS provisioner is installed."
        print_status "To install NFS provisioner, run:"
        echo "helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/"
        echo "helm repo update"
        echo "helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner --set nfs.server=<NFS_SERVER> --set nfs.path=<NFS_PATH>"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "NFS storage class found"
    fi
}

# Function to deploy manifests in order
deploy_manifests() {
    print_status "Deploying privacy-focused services..."
    
    # Deploy in order of dependencies
    manifests=(
        "00-namespace.yaml"
        "01-storage-classes.yaml"
        "02-pihole.yaml"
        "03-unbound.yaml"
        "04-whoogle.yaml"
        "05-vaultwarden.yaml"
        "06-tududi.yaml"
        "07-linkwarden.yaml"
        "08-nextcloud.yaml"
        "09-kavita.yaml"
        "10-tandoor.yaml"
        "11-n8n.yaml"
        "12-immich.yaml"
        "13-wireguard.yaml"
        "14-ingress.yaml"
    )
    
    for manifest in "${manifests[@]}"; do
        if [ -f "$manifest" ]; then
            print_status "Deploying $manifest..."
            kubectl apply -f "$manifest"
            print_success "Deployed $manifest"
        else
            print_error "Manifest file $manifest not found"
            exit 1
        fi
    done
}

# Function to wait for deployments to be ready
wait_for_deployments() {
    print_status "Waiting for deployments to be ready..."
    
    deployments=(
        "pihole"
        "unbound"
        "whoogle"
        "vaultwarden"
        "tududi"
        "linkwarden"
        "nextcloud"
        "nextcloud-db"
        "nextcloud-redis"
        "kavita"
        "tandoor"
        "tandoor-db"
        "n8n"
        "immich-server"
        "immich-microservices"
        "immich-db"
        "immich-redis"
        "wireguard"
    )
    
    for deployment in "${deployments[@]}"; do
        print_status "Waiting for $deployment..."
        kubectl wait --for=condition=available --timeout=300s deployment/$deployment -n privacy-stack || {
            print_warning "Deployment $deployment may not be ready yet"
        }
    done
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    echo
    kubectl get pods -n privacy-stack
    echo
    print_status "Services:"
    kubectl get services -n privacy-stack
    echo
    print_status "Ingress:"
    kubectl get ingress -n privacy-stack
}

# Function to show access information
show_access_info() {
    print_success "Deployment completed!"
    echo
    print_status "Access Information:"
    echo "======================"
    echo
    echo "Pi-hole (DNS & Ad-blocking):     http://pihole.local"
    echo "Whoogle (Privacy Search):        http://whoogle.local"
    echo "Vaultwarden (Password Manager):  http://vaultwarden.local"
    echo "Tududi (To-Do List):             http://tududi.local"
    echo "Linkwarden (Bookmark Manager):   http://linkwarden.local"
    echo "Nextcloud (File Sharing):        http://nextcloud.local"
    echo "Kavita (E-book Reader):          http://kavita.local"
    echo "Tandoor (Recipe Manager):        http://tandoor.local"
    echo "n8n (Workflow Automation):       http://n8n.local"
    echo "Immich (Photo Management):       http://immich.local"
    echo
    print_warning "Important Security Notes:"
    echo "==============================="
    echo "1. Change all default passwords and secrets!"
    echo "2. Configure proper SSL certificates for production use"
    echo "3. Update DNS records to point to your cluster IP"
    echo "4. Configure firewall rules as needed"
    echo "5. Review and adjust resource limits based on your hardware"
    echo
    print_status "Default Credentials (CHANGE THESE!):"
    echo "============================================"
    echo "Pi-hole Web Password:     changeme123"
    echo "Vaultwarden Admin Token:  changeme123"
    echo "Nextcloud Admin:          admin / changeme123"
    echo "n8n Basic Auth:           admin / changeme123"
    echo
    print_status "To check logs:"
    echo "kubectl logs -f deployment/<service-name> -n privacy-stack"
}

# Main execution
main() {
    print_status "Privacy-Focused Services Deployment Script"
    print_status "=========================================="
    echo
    
    check_kubectl
    check_cluster
    check_storage
    echo
    
    print_status "Starting deployment..."
    deploy_manifests
    echo
    
    print_status "Deployment completed, waiting for services to be ready..."
    wait_for_deployments
    echo
    
    show_status
    echo
    show_access_info
}

# Run main function
main "$@"
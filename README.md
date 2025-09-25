# Privacy-Focused Services Stack for K3s

This repository contains Kubernetes YAML manifests to deploy a comprehensive privacy-focused services stack on your K3s cluster with Longhorn and NFS storage support.

## 🚀 Services Included

Based on the XDA Developers article "Building Privacy-Focused Life: Docker Containers Are Non-Negotiable", this stack includes:

### Core Privacy Services
- **Pi-hole** - Network-wide ad blocker and DNS server
- **Unbound** - Validating, recursive, and caching DNS resolver
- **Whoogle** - Self-hosted, privacy-respecting metasearch engine
- **WireGuard** - Modern, fast VPN with state-of-the-art cryptography

### Productivity & Organization
- **Vaultwarden** - Self-hosted Bitwarden-compatible password manager
- **Tududi** - Self-hosted to-do list application
- **Linkwarden** - Self-hosted bookmark manager
- **Nextcloud** - Self-hosted file sharing and collaboration platform

### Media & Content
- **Kavita** - Self-hosted e-book reader and comic library manager
- **Tandoor** - Self-hosted recipe manager
- **Immich** - Self-hosted photo and video backup solution

### Automation
- **n8n** - Self-hosted workflow automation tool

## 📋 Prerequisites

### K3s Cluster
- K3s cluster running and accessible
- `kubectl` configured to connect to your cluster

### Storage Requirements
- **Longhorn** - For block storage (databases, application data)
- **NFS Storage** - For shared file storage (media files, uploads)

### Installation Commands

#### Install Longhorn
```bash
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.8.1/deploy/longhorn.yaml
```

#### Install NFS Subdir External Provisioner
```bash
# Add Helm repository
helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
helm repo update

# Install NFS provisioner (replace with your NFS server details)
helm install nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
  --set nfs.server=<NFS_SERVER_IP> \
  --set nfs.path=<NFS_SHARE_PATH>
```

## 🚀 Quick Deployment

### Automated Deployment
```bash
# Clone or download the manifests
git clone <repository-url>
cd privacy-stack

# Run the deployment script
./deploy.sh
```

### Manual Deployment
```bash
# Deploy in order
kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-storage-classes.yaml
kubectl apply -f 02-pihole.yaml
kubectl apply -f 03-unbound.yaml
kubectl apply -f 04-whoogle.yaml
kubectl apply -f 05-vaultwarden.yaml
kubectl apply -f 06-tududi.yaml
kubectl apply -f 07-linkwarden.yaml
kubectl apply -f 08-nextcloud.yaml
kubectl apply -f 09-kavita.yaml
kubectl apply -f 10-tandoor.yaml
kubectl apply -f 11-n8n.yaml
kubectl apply -f 12-immich.yaml
kubectl apply -f 13-wireguard.yaml
kubectl apply -f 14-ingress.yaml
```

## 🌐 Access Information

After deployment, services will be available at:

| Service | URL | Purpose |
|---------|-----|---------|
| Pi-hole | http://pihole.local | DNS & Ad-blocking |
| Whoogle | http://whoogle.local | Privacy-focused search |
| Vaultwarden | http://vaultwarden.local | Password manager |
| Tududi | http://tududi.local | To-do list |
| Linkwarden | http://linkwarden.local | Bookmark manager |
| Nextcloud | http://nextcloud.local | File sharing |
| Kavita | http://kavita.local | E-book reader |
| Tandoor | http://tandoor.local | Recipe manager |
| n8n | http://n8n.local | Workflow automation |
| Immich | http://immich.local | Photo management |

## 🔐 Default Credentials (CHANGE THESE!)

**⚠️ CRITICAL: Change all default passwords and secrets before production use!**

| Service | Username | Password/Token |
|---------|----------|----------------|
| Pi-hole | - | changeme123 |
| Vaultwarden | - | changeme123 |
| Nextcloud | admin | changeme123 |
| n8n | admin | changeme123 |

## 📁 Storage Configuration

### Longhorn (Block Storage)
Used for:
- Databases (PostgreSQL, MariaDB, Redis)
- Application configuration data
- Small file storage

### NFS (Shared File Storage)
Used for:
- Media files (photos, videos, books)
- File uploads
- Shared documents

## 🔧 Configuration

### DNS Configuration
Update your local DNS or `/etc/hosts` file to resolve service domains:
```
<CLUSTER_IP> pihole.local
<CLUSTER_IP> whoogle.local
<CLUSTER_IP> vaultwarden.local
<CLUSTER_IP> tududi.local
<CLUSTER_IP> linkwarden.local
<CLUSTER_IP> nextcloud.local
<CLUSTER_IP> kavita.local
<CLUSTER_IP> tandoor.local
<CLUSTER_IP> n8n.local
<CLUSTER_IP> immich.local
```

### SSL/TLS Configuration
For production use:
1. Obtain SSL certificates (Let's Encrypt recommended)
2. Update Ingress configurations to use HTTPS
3. Configure certificate secrets in Kubernetes

### Resource Limits
Adjust resource requests and limits in the manifests based on your hardware:
- **Minimum**: 4 CPU cores, 8GB RAM
- **Recommended**: 8 CPU cores, 16GB RAM
- **Storage**: 100GB+ for media files

## 🛠️ Troubleshooting

### Check Service Status
```bash
# View all pods
kubectl get pods -n privacy-stack

# Check specific service logs
kubectl logs -f deployment/<service-name> -n privacy-stack

# Describe pod for detailed information
kubectl describe pod <pod-name> -n privacy-stack
```

### Storage Issues
```bash
# Check PVC status
kubectl get pvc -n privacy-stack

# Check storage classes
kubectl get storageclass

# Check Longhorn status
kubectl get pods -n longhorn-system
```

### Network Issues
```bash
# Check services
kubectl get services -n privacy-stack

# Check ingress
kubectl get ingress -n privacy-stack

# Test service connectivity
kubectl exec -it <pod-name> -n privacy-stack -- curl <service-url>
```

## 📊 Monitoring

### Resource Usage
```bash
# Check resource usage
kubectl top pods -n privacy-stack
kubectl top nodes
```

### Longhorn Dashboard
Access Longhorn dashboard to monitor storage:
```bash
kubectl port-forward -n longhorn-system svc/longhorn-frontend 8080:80
```
Then visit: http://localhost:8080

## 🔄 Updates

### Update Services
```bash
# Update specific service
kubectl rollout restart deployment/<service-name> -n privacy-stack

# Check rollout status
kubectl rollout status deployment/<service-name> -n privacy-stack
```

### Backup Strategy
1. **Database Backups**: Use service-specific backup tools
2. **Configuration Backups**: Export Kubernetes manifests
3. **Data Backups**: Use Longhorn snapshots and NFS backups

## 🛡️ Security Considerations

1. **Change Default Credentials**: Update all default passwords and secrets
2. **Network Security**: Configure firewall rules and network policies
3. **SSL/TLS**: Enable HTTPS for all services in production
4. **Updates**: Regularly update container images and dependencies
5. **Access Control**: Implement proper RBAC and network policies
6. **Monitoring**: Set up logging and monitoring for security events

## 📝 Customization

### Environment Variables
Each service can be customized by modifying environment variables in the deployment manifests.

### Resource Allocation
Adjust CPU and memory requests/limits based on your usage patterns.

### Storage Sizes
Modify PVC sizes based on your data requirements.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- XDA Developers for the original article inspiration
- All the open-source projects that make this stack possible
- The Kubernetes and K3s communities

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review service-specific documentation
3. Open an issue in the repository
4. Join community discussions

---

**Happy self-hosting! 🎉**
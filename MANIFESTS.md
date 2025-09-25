# Kubernetes Manifests Overview

This document provides an overview of all the Kubernetes YAML manifests created for the privacy-focused services stack.

## 📁 File Structure

```
/workspace/
├── 00-namespace.yaml           # Privacy-stack namespace
├── 01-storage-classes.yaml     # Longhorn and NFS storage classes
├── 02-pihole.yaml             # Pi-hole DNS and ad-blocking
├── 03-unbound.yaml            # Unbound DNS resolver
├── 04-whoogle.yaml            # Whoogle privacy search
├── 05-vaultwarden.yaml        # Vaultwarden password manager
├── 06-tududi.yaml             # Tududi to-do list
├── 07-linkwarden.yaml         # Linkwarden bookmark manager
├── 08-nextcloud.yaml          # Nextcloud file sharing
├── 09-kavita.yaml             # Kavita e-book reader
├── 10-tandoor.yaml            # Tandoor recipe manager
├── 11-n8n.yaml                # n8n workflow automation
├── 12-immich.yaml             # Immich photo management
├── 13-wireguard.yaml          # WireGuard VPN
├── 14-ingress.yaml            # Ingress configurations
├── deploy.sh                  # Deployment script
├── README.md                  # Comprehensive documentation
└── MANIFESTS.md               # This file
```

## 🎯 Service Details

### 1. Pi-hole (`02-pihole.yaml`)
- **Purpose**: Network-wide ad blocker and DNS server
- **Image**: `pihole/pihole:2024.04.2`
- **Ports**: 80 (HTTP), 53 (DNS TCP/UDP)
- **Storage**: 2x 1Gi Longhorn PVCs
- **Access**: http://pihole.local

### 2. Unbound (`03-unbound.yaml`)
- **Purpose**: Validating, recursive, and caching DNS resolver
- **Image**: `mvance/unbound:1.19.3`
- **Ports**: 53 (DNS), 8953 (Control)
- **Storage**: 500Mi Longhorn PVC
- **Configuration**: Pre-configured with Cloudflare and Quad9 upstreams

### 3. Whoogle (`04-whoogle.yaml`)
- **Purpose**: Privacy-respecting metasearch engine
- **Image**: `benbusby/whoogle-search:0.9.2`
- **Ports**: 5000 (HTTP)
- **Storage**: 1Gi Longhorn PVC
- **Access**: http://whoogle.local

### 4. Vaultwarden (`05-vaultwarden.yaml`)
- **Purpose**: Self-hosted Bitwarden-compatible password manager
- **Image**: `vaultwarden/server:1.30.6-alpine`
- **Ports**: 80 (HTTP), 3012 (WebSocket)
- **Storage**: 5Gi Longhorn PVC
- **Access**: http://vaultwarden.local

### 5. Tududi (`06-tududi.yaml`)
- **Purpose**: Self-hosted to-do list application
- **Image**: `tududi/tududi:latest`
- **Ports**: 8080 (HTTP)
- **Storage**: 2Gi Longhorn PVC
- **Access**: http://tududi.local

### 6. Linkwarden (`07-linkwarden.yaml`)
- **Purpose**: Self-hosted bookmark manager
- **Image**: `linkwarden/linkwarden:latest`
- **Ports**: 3000 (HTTP)
- **Storage**: 5Gi + 2Gi Longhorn PVCs (app + database)
- **Database**: PostgreSQL 15
- **Access**: http://linkwarden.local

### 7. Nextcloud (`08-nextcloud.yaml`)
- **Purpose**: Self-hosted file sharing and collaboration
- **Image**: `nextcloud:27`
- **Ports**: 80 (HTTP)
- **Storage**: 50Gi NFS + 10Gi + 2Gi Longhorn PVCs
- **Database**: MariaDB 10.11
- **Cache**: Redis 7
- **Access**: http://nextcloud.local

### 8. Kavita (`09-kavita.yaml`)
- **Purpose**: Self-hosted e-book reader and comic library
- **Image**: `kizaing/kavita:latest`
- **Ports**: 5000 (HTTP)
- **Storage**: 10Gi Longhorn PVC
- **Access**: http://kavita.local

### 9. Tandoor (`10-tandoor.yaml`)
- **Purpose**: Self-hosted recipe manager
- **Image**: `vabene1111/recipes:latest`
- **Ports**: 8080 (HTTP)
- **Storage**: 5Gi + 5Gi Longhorn PVCs (app + database)
- **Database**: PostgreSQL 15
- **Access**: http://tandoor.local

### 10. n8n (`11-n8n.yaml`)
- **Purpose**: Self-hosted workflow automation
- **Image**: `n8nio/n8n:latest`
- **Ports**: 5678 (HTTP)
- **Storage**: 5Gi Longhorn PVC
- **Access**: http://n8n.local

### 11. Immich (`12-immich.yaml`)
- **Purpose**: Self-hosted photo and video backup
- **Image**: `ghcr.io/immich-app/immich:latest`
- **Ports**: 3001 (HTTP)
- **Storage**: 100Gi + 50Gi NFS + 10Gi + 2Gi Longhorn PVCs
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Access**: http://immich.local

### 12. WireGuard (`13-wireguard.yaml`)
- **Purpose**: Modern, fast VPN with state-of-the-art cryptography
- **Image**: `linuxserver/wireguard:latest`
- **Ports**: 51820 (UDP)
- **Storage**: 1Gi Longhorn PVC
- **Network**: Host network with LoadBalancer service

## 🗄️ Storage Configuration

### Longhorn Storage (Block Storage)
Used for databases and application data:
- Pi-hole: 2x 1Gi PVCs
- Unbound: 1x 500Mi PVC
- Whoogle: 1x 1Gi PVC
- Vaultwarden: 1x 5Gi PVC
- Tududi: 1x 2Gi PVC
- Linkwarden: 2x 5Gi + 2Gi PVCs
- Nextcloud: 2x 10Gi + 2Gi PVCs
- Kavita: 1x 10Gi PVC
- Tandoor: 2x 5Gi PVCs
- n8n: 1x 5Gi PVC
- Immich: 2x 10Gi + 2Gi PVCs
- WireGuard: 1x 1Gi PVC

### NFS Storage (Shared File Storage)
Used for media files and uploads:
- Nextcloud: 1x 50Gi PVC
- Immich: 2x 100Gi + 50Gi PVCs

## 🌐 Network Configuration

### Ingress (`14-ingress.yaml`)
All web services are exposed through NGINX Ingress with the following domains:
- `pihole.local`
- `whoogle.local`
- `vaultwarden.local`
- `tududi.local`
- `linkwarden.local`
- `nextcloud.local`
- `kavita.local`
- `tandoor.local`
- `n8n.local`
- `immich.local`

### Service Types
- **ClusterIP**: Internal cluster communication
- **LoadBalancer**: WireGuard VPN (external access)

## 🔧 Deployment Order

The manifests should be deployed in the following order:

1. **00-namespace.yaml** - Create namespace
2. **01-storage-classes.yaml** - Configure storage classes
3. **02-pihole.yaml** - DNS and ad-blocking
4. **03-unbound.yaml** - DNS resolver
5. **04-whoogle.yaml** - Search engine
6. **05-vaultwarden.yaml** - Password manager
7. **06-tududi.yaml** - To-do list
8. **07-linkwarden.yaml** - Bookmark manager
9. **08-nextcloud.yaml** - File sharing
10. **09-kavita.yaml** - E-book reader
11. **10-tandoor.yaml** - Recipe manager
12. **11-n8n.yaml** - Workflow automation
13. **12-immich.yaml** - Photo management
14. **13-wireguard.yaml** - VPN
15. **14-ingress.yaml** - Web access

## 🚀 Quick Deploy

Use the provided deployment script:
```bash
./deploy.sh
```

Or deploy manually:
```bash
for file in *.yaml; do
  echo "Deploying $file..."
  kubectl apply -f "$file"
done
```

## 📊 Resource Requirements

### Minimum Requirements
- **CPU**: 4 cores
- **Memory**: 8GB RAM
- **Storage**: 100GB+ (varies by usage)

### Recommended Requirements
- **CPU**: 8 cores
- **Memory**: 16GB RAM
- **Storage**: 500GB+ for media files

## 🔐 Security Notes

1. **Change Default Passwords**: All services have default credentials that must be changed
2. **SSL/TLS**: Configure HTTPS for production use
3. **Network Policies**: Implement network segmentation
4. **Updates**: Regularly update container images
5. **Backups**: Implement backup strategies for data and configurations

## 🛠️ Customization

Each manifest can be customized by modifying:
- Resource requests and limits
- Environment variables
- Storage sizes
- Network configurations
- Security settings
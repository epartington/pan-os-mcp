# TLS Termination Configuration

This document outlines the TLS termination setup for the PAN-OS MCP server using Traefik ingress in Kubernetes.

## Certificate Generation

TLS certificates are generated using `acme.sh` with Cloudflare DNS validation:

```bash
# Environment variables required
export CF_Token="your-cloudflare-token"
export CF_Zone_ID="your-cloudflare-zone-id"

# Generate certificate
acme.sh --issue --dns dns_cf -d mcp.cdot.io --server letsencrypt
```

## Kubernetes Configuration

### 1. Create TLS Secret

```bash
# Copy certificate files
mkdir -p /tmp/tls-cert
cp ~/.acme.sh/mcp.cdot.io_ecc/mcp.cdot.io.key /tmp/tls-cert/tls.key
cp ~/.acme.sh/mcp.cdot.io_ecc/fullchain.cer /tmp/tls-cert/tls.crt

# Create Kubernetes secret
kubectl create secret tls panos-mcp-tls -n panos \
  --key=/tmp/tls-cert/tls.key \
  --cert=/tmp/tls-cert/tls.crt
```

### 2. Configure Traefik Ingress

The ingress configuration in `k8s/ingress.yaml` includes:

- TLS termination using the created secret
- HTTP to HTTPS redirection
- CORS configuration
- Security headers (including HSTS)
- Rate limiting

## Certificate Renewal

Certificates will automatically renew through the `acme.sh` cron job. To manually renew:

```bash
acme.sh --renew -d mcp.cdot.io --dns dns_cf
```

## Security Features

The implementation includes:

1. TLS encryption for all API traffic
2. Network policy to restrict pod communications
3. Traefik middleware for enhanced security:
   - HTTP to HTTPS redirection
   - Security headers
   - Rate limiting
   - CORS protection

## Validation

To verify the TLS configuration:

```bash
# Check ingress status
kubectl get ingress -n panos

# Test HTTPS endpoint
curl -k https://mcp.cdot.io
```

# Deployment Guide

## Prerequisites

- Remote server with Docker installed
- Domain with DNS configured (including wildcard subdomain)
- Traefik proxy configured for HTTPS

## Environment Setup

### Required Environment Variables
```bash
ENVIRONMENT=production
DOMAIN=your-domain.com
STACK_NAME=your-stack-name
SECRET_KEY=<generated-secret>
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=<secure-password>
POSTGRES_PASSWORD=<secure-password>
BACKEND_CORS_ORIGINS=https://dashboard.your-domain.com
FRONTEND_HOST=https://dashboard.your-domain.com
```

### Generate Secrets
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Traefik Setup (One-time)

1. Create Traefik directory:
```bash
mkdir -p /root/code/traefik-public/
```

2. Copy Traefik config:
```bash
rsync -a docker-compose.traefik.yml root@server:/root/code/traefik-public/
```

3. Create Docker network:
```bash
docker network create traefik-public
```

4. Set environment variables and start:
```bash
export USERNAME=admin
export PASSWORD=changethis
export HASHED_PASSWORD=$(openssl passwd -apr1 $PASSWORD)
export DOMAIN=your-domain.com
export EMAIL=admin@example.com
cd /root/code/traefik-public/
docker compose -f docker-compose.traefik.yml up -d
```

## Manual Deployment

```bash
docker compose -f docker-compose.yml up -d
```

## CI/CD with GitHub Actions

### Setup GitHub Actions Runner
1. Create `github` user on server
2. Add Docker permissions: `sudo usermod -aG docker github`
3. Install self-hosted runner (follow GitHub guide)
4. Install as service: `./svc.sh install github`

### Configure GitHub Secrets
Set these in repository settings:
- `DOMAIN_PRODUCTION` / `DOMAIN_STAGING`
- `STACK_NAME_PRODUCTION` / `STACK_NAME_STAGING`
- `SECRET_KEY`
- `FIRST_SUPERUSER` / `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`
- `EMAILS_FROM_EMAIL`

### Deployment Triggers
- **Staging**: Automatic on push to `master` branch
- **Production**: Automatic on release publication

## Production URLs

- Frontend: `https://dashboard.your-domain.com`
- Backend API: `https://api.your-domain.com`
- API Docs: `https://api.your-domain.com/docs`
- Adminer: `https://adminer.your-domain.com`
- Traefik: `https://traefik.your-domain.com`

## Monitoring

- Check logs: `docker compose logs -f`
- Check service status: `docker compose ps`
- Traefik dashboard for routing info

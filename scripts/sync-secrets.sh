#!/bin/bash
# Sync secrets from .env to GitHub repository secrets
# Usage: ./scripts/sync-secrets.sh [env_file]

ENV_FILE="${1:-.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: $ENV_FILE not found"
  exit 1
fi

# Check gh is installed and authenticated
if ! command -v gh &> /dev/null; then
  echo "Error: GitHub CLI (gh) is not installed"
  echo "Install: https://cli.github.com/"
  exit 1
fi

if ! gh auth status &> /dev/null; then
  echo "Error: Not authenticated with GitHub CLI"
  echo "Run: gh auth login"
  exit 1
fi

# Secrets to sync - format: "GITHUB_SECRET_NAME:ENV_VAR_NAME" or just "NAME" if same
SECRETS=(
  "DOMAIN_STAGING:DOMAIN"
  "DOMAIN_PRODUCTION:DOMAIN"
  "STACK_NAME_STAGING:STACK_NAME"
  "STACK_NAME_PRODUCTION:STACK_NAME"
  "SECRET_KEY"
  "FIRST_SUPERUSER"
  "FIRST_SUPERUSER_PASSWORD"
  "POSTGRES_PASSWORD"
  "SMTP_HOST"
  "SMTP_USER"
  "SMTP_PASSWORD"
  "EMAILS_FROM_EMAIL"
  "SENTRY_DSN"
  "DOCKER_IMAGE_BACKEND"
  "DOCKER_IMAGE_FRONTEND"
)

echo "Syncing secrets from $ENV_FILE to GitHub..."
echo ""

synced=0
skipped=0

for entry in "${SECRETS[@]}"; do
  # Parse "GITHUB_NAME:ENV_NAME" or just "NAME"
  if [[ "$entry" == *":"* ]]; then
    github_name="${entry%%:*}"
    env_name="${entry##*:}"
  else
    github_name="$entry"
    env_name="$entry"
  fi
  
  # Extract value from .env (handles quotes and spaces)
  value=$(grep "^${env_name}=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2- | sed 's/^["'"'"']//;s/["'"'"']$//')
  
  if [[ -n "$value" ]]; then
    echo "Setting $github_name (from $env_name)..."
    if gh secret set "$github_name" --body "$value"; then
      ((synced++))
    else
      echo "  Failed to set $github_name"
    fi
  else
    echo "Skipping $github_name ($env_name not found or empty)"
    ((skipped++))
  fi
done

echo ""
echo "Done! Synced: $synced, Skipped: $skipped"

# GitHub Actions Secrets Setup

## Required Secrets

Configure these secrets in your GitHub repository settings:

**Repository Settings → Secrets and variables → Actions → New repository secret**

### Azure Credentials

```bash
# Generate Azure credentials
az ad sp create-for-rbac \
  --name "github-actions-aks" \
  --role contributor \
  --scopes /subscriptions/<subscription-id>/resourceGroups/todo-rg \
  --sdk-auth

# Copy the JSON output and add as AZURE_CREDENTIALS secret
```

**Secret Name:** `AZURE_CREDENTIALS`  
**Value:** JSON output from above command

---

### Database Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DB_USERNAME` | PostgreSQL admin username | `postgres` |
| `DB_PASSWORD` | PostgreSQL admin password | `SecureP@ssw0rd123!` |
| `DB_HOST` | PostgreSQL server hostname | `todo-postgres-server.postgres.database.azure.com` |
| `DB_PORT` | PostgreSQL port | `5432` |

---

### Redis Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `REDIS_PASSWORD` | Redis access password | `RedisP@ssw0rd!` |
| `REDIS_HOST` | Redis hostname | `todo-redis.redis.cache.windows.net` |

---

### Email/SMTP Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SMTP_HOST` | SMTP server hostname | `smtp.office365.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USERNAME` | SMTP username | `noreply@todo-chatbot.com` |
| `SMTP_PASSWORD` | SMTP password | `EmailP@ssw0rd!` |

---

### Push Notification Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `FIREBASE_API_KEY` | Firebase Cloud Messaging API key | `AAAA...` |

---

### Notification Secrets (Optional)

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL | `https://hooks.slack.com/services/...` |
| `NOTIFICATION_EMAIL` | Email for deployment notifications | `team@todo-chatbot.com` |
| `VERCEL_TOKEN` | Vercel deployment token | `...` |

---

## Environment Configuration

### Production Environment

1. Go to **Repository Settings → Environments**
2. Click **New environment**
3. Name: `production`
4. Configure:
   - **Deployment branches:** `main` only
   - **Required reviewers:** Add team members for approval
   - **Environment secrets:** Override any secrets for production

### Development Environment (Optional)

1. Create environment: `develop`
2. Configure:
   - **Deployment branches:** `develop`
   - **No required reviewers** (for faster iteration)

---

## GitHub Container Registry

The workflow uses GitHub Container Registry (GHCR) automatically with `GITHUB_TOKEN`.

**Image URLs:**
- `ghcr.io/<org>/todo-chatbot/chat-api`
- `ghcr.io/<org>/todo-chatbot/recurring-service`
- `ghcr.io/<org>/todo-chatbot/notification-service`

**Access images:**
```bash
docker login ghcr.io -u <github-username> -p <github-token>
docker pull ghcr.io/<org>/todo-chatbot/chat-api:latest
```

---

## Verification

After configuring secrets, verify the workflow:

1. Push to `main` branch or create a tag
2. Go to **Actions** tab
3. Select "Phase V - Deploy to AKS" workflow
4. Verify all jobs complete successfully

---

## Security Best Practices

1. **Use OIDC (OpenID Connect)** instead of long-lived credentials:
   ```bash
   az ad federated-identity-credential create \
     --resource-group todo-rg \
     --name github-actions \
     --issuer https://token.actions.githubusercontent.com \
     --subject repo:<org>/<repo>:ref:refs/heads/main
   ```

2. **Rotate secrets regularly** (every 90 days recommended)

3. **Use environment-specific secrets** for dev/staging/production

4. **Limit secret access** to specific workflows using `environment` protection rules

5. **Audit secret usage** in GitHub Actions logs

---

## Troubleshooting

### Workflow Fails at Azure Login

- Verify `AZURE_CREDENTIALS` secret is valid JSON
- Check service principal has contributor role
- Ensure subscription is not expired

### Kubernetes Deployment Fails

- Verify AKS cluster name and resource group
- Check kubectl can connect to cluster
- Verify secrets are created in correct namespace

### Helm Deploy Fails

- Check Helm chart syntax: `helm lint ./helm`
- Verify values files exist
- Test locally: `helm upgrade --install todo-app ./helm --dry-run --debug`

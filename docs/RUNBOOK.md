# Clankerbot Runbook

Operations guide for running and maintaining Clankerbot in production.

## Deployment

### Docker Compose (Recommended)

```bash
# 1. Clone repository
git clone <repo-url> clankerbot
cd clankerbot

# 2. Create .env file
cp .env.example .env
# Edit .env with your credentials

# 3. Start service
docker compose up -d

# 4. Check health
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
```

### Docker

```bash
# Build
docker build -t clankerbot:latest .

# Run
docker run -d \
  -p 8000:8000 \
  -e CLOCKIFY_API_KEY=your_key \
  -e DEEPSEEK_API_KEY=your_key \
  --name clankerbot \
  clankerbot:latest
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export CLOCKIFY_API_KEY=your_key
export DEEPSEEK_API_KEY=your_key

# Run server
uvicorn app.main:app --reload --port 8000
```

## Configuration

### Required Environment Variables

```bash
# Clockify (at least one required)
CLOCKIFY_API_KEY=sk_xxx              # User API key
# OR
CLOCKIFY_ADDON_TOKEN=addon_xxx       # Addon token

# LLM (optional, required for llm=true parsing)
DEEPSEEK_API_KEY=sk_xxx
```

### Optional Environment Variables

```bash
# LLM Configuration
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# Clockify Configuration
CLOCKIFY_BASE_URL=https://api.clockify.me/api

# Security
WEBHOOK_SHARED_SECRET=my_secret_123   # Enable webhook authentication
RATE_LIMIT_PER_MINUTE=60              # Requests per minute per IP+path

# Observability
LOG_JSON=true                          # Enable JSON logging
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318

# Server
CORS_ORIGINS=http://localhost:3000,https://app.example.com
```

## Operations

### Rotating API Keys

#### Clockify API Key

```bash
# 1. Generate new key in Clockify web UI (Settings → API)
# 2. Update environment variable
#    Docker Compose: Edit .env, then:
docker compose down
docker compose up -d

#    Kubernetes: Update secret, rollout restart
kubectl create secret generic clankerbot-secrets \
  --from-literal=clockify-api-key=NEW_KEY \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl rollout restart deployment/clankerbot
```

#### DeepSeek API Key

Same procedure as Clockify, use DEEPSEEK_API_KEY

### Changing Rate Limits

```bash
# Update RATE_LIMIT_PER_MINUTE in .env
RATE_LIMIT_PER_MINUTE=120

# Restart service
docker compose restart
```

### Handling 429 Rate Limit Errors

#### From Clockify API

Clankerbot automatically retries 3 times with backoff. If still failing:

1. Check Clockify plan limits
2. Reduce request frequency
3. Contact Clockify support for higher limits

#### From Clankerbot (self-imposed)

Clients receive 429 with error code "rate_limited". Solutions:

1. Increase RATE_LIMIT_PER_MINUTE
2. Implement client-side backoff
3. Distribute load across multiple IPs

### Webhook Setup

#### 1. Configure Secret (Recommended)

```bash
# Generate secret
SECRET=$(openssl rand -hex 32)
echo "WEBHOOK_SHARED_SECRET=$SECRET" >> .env

# Restart
docker compose restart
```

#### 2. Register Webhook in Clockify

1. Go to Clockify → Settings → Webhooks
2. Add webhook URL: `https://your-domain.com/webhooks/clockify`
3. Add custom header: `X-Webhook-Secret: <your_secret>`
4. Select events to subscribe
5. Save

#### 3. Test Webhook

```bash
# Trigger test event in Clockify, check logs:
docker compose logs -f clankerbot

# Or send manual test:
curl -X POST https://your-domain.com/webhooks/clockify \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your_secret" \
  -H "X-Clockify-Event-Id: test_123" \
  -d '{"id": "test", "workspaceId": "ws123", "userId": "user123"}'
```

## Monitoring

### Health Checks

```bash
# Basic health (always returns ok if app is running)
curl http://localhost:8000/healthz

# Readiness (checks dependencies)
curl http://localhost:8000/readyz
# Returns: {"ok": true, "data": {"ready": true, "checks": {"llm": "configured", "clockify": "configured"}}}
```

### Logs

```bash
# Docker Compose
docker compose logs -f

# Docker
docker logs -f clankerbot

# JSON logs (if LOG_JSON=true)
docker compose logs clankerbot | jq .
```

### Key Metrics to Monitor

1. **Request rate**: Monitor via X-Request-ID in logs
2. **Error rate**: Count ApiResponse with ok=false
3. **LLM fallback rate**: Count parser="fallback" in /actions/parse responses
4. **Webhook duplicates**: Count duplicate=true in webhook responses
5. **429 errors**: Both self-imposed and from Clockify

## Troubleshooting

### LLM Parsing Always Falls Back

**Symptoms**: All llm=true requests return parser="fallback"

**Checks**:
1. `curl /readyz` → Check if llm="configured"
2. Verify DEEPSEEK_API_KEY is set and valid
3. Check logs for "LLM parsing failed" warnings
4. Test API key manually:
   ```bash
   curl https://api.deepseek.com/chat/completions \
     -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}]}'
   ```

### Clockify Actions Fail with "unauthorized"

**Symptoms**: /actions/run returns error code "unauthorized"

**Checks**:
1. `curl /readyz` → Check if clockify="configured"
2. Verify CLOCKIFY_API_KEY or CLOCKIFY_ADDON_TOKEN is set
3. Test key manually:
   ```bash
   curl https://api.clockify.me/api/v1/user \
     -H "X-Api-Key: $CLOCKIFY_API_KEY"
   ```

### Webhook Returns 401

**Symptoms**: POST /webhooks/clockify returns unauthorized

**Cause**: WEBHOOK_SHARED_SECRET is set but X-Webhook-Secret header missing/wrong

**Fix**:
- Add correct X-Webhook-Secret header to webhook calls
- OR remove WEBHOOK_SHARED_SECRET from env to disable validation

### High Memory Usage

**Symptoms**: Container OOM or high memory usage

**Possible causes**:
1. Webhook event cache growing (max 1000 entries)
2. Rate limit buckets accumulating (1 per IP+path)

**Mitigations**:
- Restart service to clear caches
- In production, move to Redis-backed caching

### Rate Limit Hit Frequently

**Symptoms**: Frequent 429 responses

**Solutions**:
1. Increase RATE_LIMIT_PER_MINUTE
2. Check if traffic is legitimate (review logs by IP)
3. Implement upstream rate limiting (nginx, API gateway)

## Backups and Disaster Recovery

Clankerbot is stateless. No backups needed.

**To restore**:
1. Redeploy from git
2. Set environment variables
3. Reconfigure webhooks in Clockify

## Security Incidents

### API Key Leaked

1. **Immediate**: Rotate key (see "Rotating API Keys")
2. **Investigate**: Check logs for unauthorized usage
3. **Notify**: Alert team, consider Clockify support if needed

### Unauthorized Access to Webhooks

1. **Immediate**: Enable WEBHOOK_SHARED_SECRET if not set
2. **Investigate**: Check logs for suspicious IPs
3. **Mitigate**: Add IP allowlist at reverse proxy level

## Performance Tuning

### Reduce LLM Latency

- Use faster LLM model (if available)
- Reduce LLM timeout (default 20s)
- Disable LLM parsing if not needed (llm=false)

### Reduce Clockify Latency

- Use regional Clockify URL if available (CLOCKIFY_BASE_URL)
- Optimize retry logic (adjust max_retries in code)

### Scale Horizontally

```bash
# Docker Compose: Scale to 3 replicas
docker compose up -d --scale clankerbot=3

# Kubernetes: Scale deployment
kubectl scale deployment/clankerbot --replicas=3
```

**Note**: For multi-instance deployments, migrate webhook cache and rate limiter to Redis.

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster 1.24+
- kubectl configured to access your cluster
- Helm 3.10+ (for Helm installation)
- Docker image built and pushed to registry

### Option 1: kubectl (Raw Manifests)

#### Initial Deployment

```bash
# 1. Create namespace (optional but recommended)
kubectl create namespace clankerbot

# 2. Create secrets with your API keys
kubectl create secret generic clankerbot-secrets \
  --from-literal=clockify-api-key=your_clockify_api_key \
  --from-literal=deepseek-api-key=your_deepseek_api_key \
  --from-literal=webhook-shared-secret=$(openssl rand -hex 32) \
  -n clankerbot

# 3. Apply manifests
kubectl apply -f deploy/k8s/ -n clankerbot

# 4. Verify deployment
kubectl get all -n clankerbot

# Expected output:
# - 2 pods running
# - 1 service (ClusterIP)
# - 1 deployment

# 5. Check pod status
kubectl get pods -n clankerbot
# Both pods should be Running with 1/1 ready

# 6. View logs
kubectl logs -f deployment/clankerbot -n clankerbot
```

#### Update ConfigMap

```bash
# Edit configmap
kubectl edit configmap clankerbot-config -n clankerbot

# Or apply changes
kubectl apply -f deploy/k8s/configmap.yaml -n clankerbot

# Restart pods to pick up changes
kubectl rollout restart deployment/clankerbot -n clankerbot
```

#### Update Secrets

```bash
# Update secret (e.g., rotating API key)
kubectl create secret generic clankerbot-secrets \
  --from-literal=clockify-api-key=new_api_key \
  --from-literal=deepseek-api-key=your_deepseek_key \
  --from-literal=webhook-shared-secret=your_secret \
  --dry-run=client -o yaml | kubectl apply -f - -n clankerbot

# Restart to pick up new secrets
kubectl rollout restart deployment/clankerbot -n clankerbot
```

#### Scale Deployment

```bash
# Scale to 5 replicas
kubectl scale deployment/clankerbot --replicas=5 -n clankerbot

# Verify scaling
kubectl get pods -n clankerbot
```

#### Expose via Ingress

```bash
# 1. Edit ingress.yaml to set your domain
nano deploy/k8s/ingress.yaml
# Change clankerbot.example.com to your domain

# 2. Apply ingress
kubectl apply -f deploy/k8s/ingress.yaml -n clankerbot

# 3. Verify ingress
kubectl get ingress -n clankerbot
kubectl describe ingress clankerbot -n clankerbot

# 4. Test endpoint (after DNS propagation)
curl https://your-domain.com/healthz
```

#### Port Forward for Testing

```bash
# Forward local port 8000 to service
kubectl port-forward -n clankerbot svc/clankerbot 8000:8000

# In another terminal, test
curl http://localhost:8000/healthz
```

#### View Logs

```bash
# All pods
kubectl logs -f deployment/clankerbot -n clankerbot

# Specific pod
kubectl logs -f pod/clankerbot-xyz123 -n clankerbot

# Last 100 lines
kubectl logs --tail=100 deployment/clankerbot -n clankerbot

# Follow logs from all replicas
kubectl logs -f -l app=clankerbot -n clankerbot
```

#### Delete Deployment

```bash
kubectl delete -f deploy/k8s/ -n clankerbot
kubectl delete secret clankerbot-secrets -n clankerbot
kubectl delete namespace clankerbot
```

### Option 2: Helm Chart

#### Initial Installation

```bash
# 1. Create namespace
kubectl create namespace clankerbot

# 2. Install chart with inline secrets
helm install clankerbot ./deploy/helm/clankerbot \
  --namespace clankerbot \
  --set secrets.clockifyApiKey=your_clockify_key \
  --set secrets.deepseekApiKey=your_deepseek_key \
  --set secrets.webhookSharedSecret=$(openssl rand -hex 32) \
  --set image.tag=latest

# 3. Verify installation
helm status clankerbot -n clankerbot
kubectl get pods -n clankerbot
```

#### Production Installation with Custom Values

```bash
# 1. Create production values file
cat > production-values.yaml <<EOF
replicaCount: 3

image:
  repository: registry.example.com/clankerbot
  tag: "0.2.0"
  pullPolicy: IfNotPresent

secrets:
  clockifyApiKey: "your_clockify_key"
  deepseekApiKey: "your_deepseek_key"
  webhookSharedSecret: "randomly_generated_secret_at_least_32_chars"

config:
  rateLimitPerMinute: 120
  logJson: true
  corsOrigins: "https://app.example.com,https://admin.example.com"

resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "500m"

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/limit-rps: "30"
  hosts:
    - host: clankerbot.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: clankerbot-tls
      hosts:
        - clankerbot.example.com

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

nodeSelector:
  workload: api

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app.kubernetes.io/name
            operator: In
            values:
            - clankerbot
        topologyKey: kubernetes.io/hostname
EOF

# 2. Install with production values
helm install clankerbot ./deploy/helm/clankerbot \
  -f production-values.yaml \
  --namespace clankerbot

# 3. Verify
helm status clankerbot -n clankerbot
```

#### Upgrade Deployment

```bash
# Upgrade to new version
helm upgrade clankerbot ./deploy/helm/clankerbot \
  -f production-values.yaml \
  --namespace clankerbot

# Upgrade with new image tag
helm upgrade clankerbot ./deploy/helm/clankerbot \
  --set image.tag=0.2.1 \
  --namespace clankerbot

# Upgrade and force pod restart
helm upgrade clankerbot ./deploy/helm/clankerbot \
  --set image.tag=0.2.1 \
  --force \
  --namespace clankerbot
```

#### Rollback

```bash
# List releases
helm history clankerbot -n clankerbot

# Rollback to previous version
helm rollback clankerbot -n clankerbot

# Rollback to specific revision
helm rollback clankerbot 2 -n clankerbot
```

#### Update Configuration

```bash
# Update values and upgrade
helm upgrade clankerbot ./deploy/helm/clankerbot \
  --set config.rateLimitPerMinute=200 \
  --namespace clankerbot

# Or edit values file and upgrade
helm upgrade clankerbot ./deploy/helm/clankerbot \
  -f production-values.yaml \
  --namespace clankerbot
```

#### View Values

```bash
# View current values
helm get values clankerbot -n clankerbot

# View all values (including defaults)
helm get values clankerbot -n clankerbot --all
```

#### Uninstall

```bash
helm uninstall clankerbot -n clankerbot
kubectl delete namespace clankerbot
```

### Kubernetes Best Practices

#### Resource Limits

```yaml
# Recommended resource settings
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

#### Horizontal Pod Autoscaling

```bash
# Enable HPA in Helm
helm upgrade clankerbot ./deploy/helm/clankerbot \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10 \
  --namespace clankerbot

# Monitor HPA
kubectl get hpa -n clankerbot
kubectl describe hpa clankerbot -n clankerbot
```

#### Pod Disruption Budget

```yaml
# Create PDB for high availability
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: clankerbot-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: clankerbot
```

```bash
kubectl apply -f pdb.yaml -n clankerbot
```

#### Network Policies (Optional)

```yaml
# Restrict ingress to only from ingress controller
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: clankerbot-netpol
spec:
  podSelector:
    matchLabels:
      app: clankerbot
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
```

### Monitoring in Kubernetes

#### Health Checks

```bash
# Check liveness
kubectl exec -it deployment/clankerbot -n clankerbot -- \
  curl http://localhost:8000/healthz

# Check readiness
kubectl exec -it deployment/clankerbot -n clankerbot -- \
  curl http://localhost:8000/readyz
```

#### Pod Events

```bash
# View pod events
kubectl describe pod clankerbot-xyz -n clankerbot

# Watch events
kubectl get events -n clankerbot --watch
```

#### Resource Usage

```bash
# View resource usage (requires metrics-server)
kubectl top pods -n clankerbot
kubectl top nodes
```

### Troubleshooting Kubernetes Deployments

#### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n clankerbot

# Describe pod for events
kubectl describe pod clankerbot-xyz -n clankerbot

# Check logs
kubectl logs clankerbot-xyz -n clankerbot

# Common causes:
# - Image pull errors: Check image name and pull policy
# - Secrets missing: Verify clankerbot-secrets exists
# - Resource limits: Check if node has available resources
```

#### Pods Restarting

```bash
# Check restart count
kubectl get pods -n clankerbot

# View previous logs (from crashed container)
kubectl logs clankerbot-xyz -n clankerbot --previous

# Check liveness/readiness probes
kubectl describe pod clankerbot-xyz -n clankerbot | grep -A 10 Probes

# Common causes:
# - OOM killed: Increase memory limits
# - Failing health checks: Check /healthz and /readyz endpoints
# - API key issues: Verify secrets are correct
```

#### Ingress Not Working

```bash
# Check ingress status
kubectl get ingress -n clankerbot
kubectl describe ingress clankerbot -n clankerbot

# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Verify service endpoints
kubectl get endpoints clankerbot -n clankerbot

# Common causes:
# - DNS not configured: Check domain points to ingress IP
# - TLS secret missing: Check cert-manager or create manual secret
# - Ingress class wrong: Verify ingressClassName matches your controller
```

#### Service Not Accessible

```bash
# Check service
kubectl get svc clankerbot -n clankerbot
kubectl describe svc clankerbot -n clankerbot

# Check endpoints (should match pod IPs)
kubectl get endpoints clankerbot -n clankerbot

# Test service from another pod
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://clankerbot.clankerbot.svc.cluster.local:8000/healthz
```

#### ConfigMap/Secret Not Applied

```bash
# Verify configmap
kubectl get configmap clankerbot-config -n clankerbot -o yaml

# Verify secret
kubectl get secret clankerbot-secrets -n clankerbot -o yaml

# After updating, restart pods
kubectl rollout restart deployment/clankerbot -n clankerbot

# Wait for rollout to complete
kubectl rollout status deployment/clankerbot -n clankerbot
```

## Support

- **Issues**: https://github.com/your-org/clankerbot/issues
- **Docs**: See README.md, ARCH.md
- **Clockify API**: https://clockify.me/developers-api

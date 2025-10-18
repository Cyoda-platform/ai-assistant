# Helm Chart - GitHub App Private Key Support

## ✅ Complete Implementation

The Helm chart now fully supports **both methods** for providing the GitHub App private key to Kubernetes deployments.

---

## What Was Added

### 1. **Code Support for Both Options**

#### File: `services/github/auth/jwt_generator.py`
- ✅ Supports loading PEM from **file path** (`GITHUB_APP_PRIVATE_KEY_PATH`)
- ✅ Supports loading PEM from **environment variable** (`GITHUB_APP_PRIVATE_KEY_CONTENT`)
- ✅ Automatic fallback: tries env variable first, then file path

#### File: `common/config/config.py`
- ✅ Added `GITHUB_APP_PRIVATE_KEY_CONTENT` configuration variable

### 2. **Helm Chart Updates**

#### File: `helm/charts/ai-assistant/values.yaml`
```yaml
githubApp:
  privateKey:
    mountFromSecret: false      # Enable to mount PEM file as volume
    secretName: "github-app-private-key"
    secretKey: "private-key.pem"
    mountPath: "/secrets"
```

#### File: `helm/charts/ai-assistant/templates/deployment.yaml`
- ✅ Conditional volume mount for PEM file
- ✅ Conditional volume mount in container
- ✅ Proper file permissions (0400)

### 3. **Documentation**

#### Created Files:
- ✅ `helm/charts/ai-assistant/README.md` - Complete Helm chart documentation
- ✅ `helm/charts/ai-assistant/values-production-example.yaml` - Production example
- ✅ `helm/charts/ai-assistant/deploy.sh` - Deployment helper script
- ✅ `KUBERNETES_DEPLOYMENT_GUIDE.md` - Comprehensive Kubernetes guide

---

## Usage

### Option 1: Volume Mount (Recommended)

#### Step 1: Create Secret
```bash
kubectl create secret generic github-app-private-key \
  --from-file=private-key.pem=./private-key.pem \
  --namespace=your-namespace
```

#### Step 2: Configure values.yaml
```yaml
githubApp:
  privateKey:
    mountFromSecret: true
    secretName: "github-app-private-key"
    mountPath: "/secrets"

container:
  env:
    vars:
      GITHUB_APP_PRIVATE_KEY_PATH: "/secrets/private-key.pem"
```

#### Step 3: Deploy
```bash
helm install ai-assistant ./helm/charts/ai-assistant \
  --namespace=your-namespace \
  --values=values-production.yaml
```

**OR use the helper script:**
```bash
cd helm/charts/ai-assistant
./deploy.sh -n production -p ./private-key.pem -v values-production.yaml
```

---

### Option 2: Environment Variable

#### Step 1: Create Secret
```bash
kubectl create secret generic github-app-credentials \
  --from-literal=private-key-content="$(cat private-key.pem)" \
  --namespace=your-namespace
```

#### Step 2: Configure values.yaml
```yaml
githubApp:
  privateKey:
    mountFromSecret: false

container:
  env:
    secretVars:
      GITHUB_APP_PRIVATE_KEY_CONTENT: "base64-encoded-pem-content"
```

#### Step 3: Deploy
```bash
helm install ai-assistant ./helm/charts/ai-assistant \
  --namespace=your-namespace \
  --values=values-production.yaml
```

**OR use the helper script:**
```bash
cd helm/charts/ai-assistant
./deploy.sh -n production -p ./private-key.pem -o env
```

---

## Comparison

| Feature | Volume Mount | Environment Variable |
|---------|--------------|---------------------|
| **Security** | ✅ More secure | ⚠️ Less secure |
| **File Permissions** | ✅ 0400 (read-only) | ❌ N/A |
| **Visibility** | ✅ Not in pod spec | ❌ Visible in pod spec |
| **Rotation** | ✅ Easier | ⚠️ Harder |
| **Setup Complexity** | ⚠️ Requires volume | ✅ Simpler |
| **Best For** | Production | Development/Testing |

---

## Helper Script Usage

The `deploy.sh` script simplifies deployment:

```bash
# Show help
./deploy.sh --help

# Deploy with volume mount (recommended)
./deploy.sh -n production -p ./private-key.pem -v values-production.yaml

# Deploy with environment variable
./deploy.sh -n dev -p ./private-key.pem -o env

# Dry run
./deploy.sh -n production -p ./private-key.pem -v values-production.yaml --dry-run
```

**Script Features:**
- ✅ Automatically creates namespace
- ✅ Creates appropriate secret based on option
- ✅ Validates inputs
- ✅ Supports dry-run mode
- ✅ Colored output for better readability
- ✅ Shows deployment status

---

## Verification

### Check if PEM file is loaded correctly

```bash
# View logs
kubectl logs -f deployment/ai-assistant -n your-namespace

# Look for one of these messages:
# ✅ "Successfully loaded GitHub App private key from /secrets/private-key.pem"
# ✅ "Successfully loaded GitHub App private key from environment variable"
```

### Check secret exists

```bash
# For volume mount option
kubectl get secret github-app-private-key -n your-namespace

# For environment variable option
kubectl get secret github-app-credentials -n your-namespace
```

### Check volume is mounted (volume mount option only)

```bash
kubectl exec -it deployment/ai-assistant -n your-namespace -- ls -la /secrets/
# Should show: -r-------- 1 root root ... private-key.pem
```

### Verify secret content

```bash
# For volume mount
kubectl get secret github-app-private-key -n your-namespace \
  -o jsonpath='{.data.private-key\.pem}' | base64 -d | head -1
# Should show: -----BEGIN RSA PRIVATE KEY-----

# For environment variable
kubectl get secret github-app-credentials -n your-namespace \
  -o jsonpath='{.data.private-key-content}' | base64 -d | head -1
# Should show: -----BEGIN RSA PRIVATE KEY-----
```

---

## Production Best Practices

### 1. Use Volume Mount
```yaml
githubApp:
  privateKey:
    mountFromSecret: true
```

### 2. Enable RBAC
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["github-app-private-key"]
  verbs: ["get"]
```

### 3. Use External Secrets Operator
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: github-app-secret
spec:
  secretStoreRef:
    name: aws-secrets-manager
  data:
  - secretKey: private-key.pem
    remoteRef:
      key: github-app-private-key
```

### 4. Set Security Context
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  readOnlyRootFilesystem: false
```

### 5. Enable Autoscaling
```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

---

## Files Modified/Created

### Modified:
- ✅ `services/github/auth/jwt_generator.py` - Added env variable support
- ✅ `common/config/config.py` - Added GITHUB_APP_PRIVATE_KEY_CONTENT
- ✅ `helm/charts/ai-assistant/values.yaml` - Added githubApp configuration
- ✅ `helm/charts/ai-assistant/templates/deployment.yaml` - Added volume mount support
- ✅ `.env.template` - Added GITHUB_APP_PRIVATE_KEY_CONTENT

### Created:
- ✅ `helm/charts/ai-assistant/README.md` - Helm chart documentation
- ✅ `helm/charts/ai-assistant/values-production-example.yaml` - Production example
- ✅ `helm/charts/ai-assistant/deploy.sh` - Deployment helper script
- ✅ `KUBERNETES_DEPLOYMENT_GUIDE.md` - Comprehensive Kubernetes guide
- ✅ `HELM_CHART_GITHUB_APP_SUPPORT.md` - This document

---

## Testing

Both options have been tested and verified:

```bash
✅ Test 1: Loading from file path - PASSED
✅ Test 2: Loading from environment variable - PASSED
✅ Keys match: True
```

---

## Summary

✅ **Code supports both options** (file path and environment variable)  
✅ **Helm chart supports both options** (volume mount and env var)  
✅ **Complete documentation** (README, examples, guides)  
✅ **Helper script** for easy deployment  
✅ **Production-ready** with security best practices  
✅ **Tested and verified** both options work correctly  

**Your Helm chart is now ready for production deployment with GitHub App private key support!** 🚀

---

## Quick Start

```bash
# 1. Navigate to Helm chart directory
cd helm/charts/ai-assistant

# 2. Deploy to production (volume mount - recommended)
./deploy.sh -n production -p /path/to/private-key.pem -v values-production.yaml

# 3. Verify deployment
kubectl get pods -n production
kubectl logs -f deployment/ai-assistant -n production
```

**Done!** 🎉


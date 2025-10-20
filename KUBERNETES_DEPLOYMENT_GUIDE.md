# Kubernetes Deployment Guide - GitHub App Private Key

## Overview

This guide shows how to securely deploy the AI Assistant application to Kubernetes with the GitHub App private key.

---

## ⚠️ Important: Use Secrets, Not ConfigMaps

**ConfigMaps** are for **non-sensitive** configuration data.  
**Secrets** are for **sensitive** data like private keys, passwords, tokens.

✅ **Use Kubernetes Secret** for the PEM file  
❌ **Do NOT use ConfigMap** for the PEM file

---

## Option 1: Mount PEM File as Volume (Recommended)

This is the most secure and straightforward approach.

### Step 1: Create Secret from PEM File

```bash
# Create secret from your private-key.pem file
kubectl create secret generic github-app-private-key \
  --from-file=private-key.pem=./private-key.pem \
  --namespace=your-namespace

# Verify secret was created
kubectl get secret github-app-private-key -n your-namespace
```

### Step 2: Update Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-assistant
  namespace: your-namespace
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ai-assistant
  template:
    metadata:
      labels:
        app: ai-assistant
    spec:
      containers:
      - name: ai-assistant
        image: your-registry/ai-assistant:latest
        
        # Environment variables
        env:
        - name: GITHUB_APP_ID
          value: "2134377"
        - name: GITHUB_APP_OWNER
          value: "Cyoda-platform"
        - name: GITHUB_APP_CLIENT_ID
          value: "Iv23liau2M4692QS4yzR"
        - name: GITHUB_APP_PRIVATE_KEY_PATH
          value: "/secrets/private-key.pem"  # Path where secret will be mounted
        - name: GITHUB_PUBLIC_REPO_INSTALLATION_ID
          value: "90584123"
        - name: PYTHON_PUBLIC_REPO_URL
          value: "https://github.com/Cyoda-platform/mcp-cyoda-quart-app"
        - name: JAVA_PUBLIC_REPO_URL
          value: "https://github.com/Cyoda-platform/java-client-template"
        
        # Mount the secret as a volume
        volumeMounts:
        - name: github-app-key
          mountPath: "/secrets"
          readOnly: true
        
        ports:
        - containerPort: 8080
      
      # Define the secret volume
      volumes:
      - name: github-app-key
        secret:
          secretName: github-app-private-key
          defaultMode: 0440  # Read-only for owner and group (octal)
```

### Step 3: Apply Deployment

```bash
kubectl apply -f deployment.yaml
```

### Step 4: Verify

```bash
# Check pod is running
kubectl get pods -n your-namespace

# Check logs
kubectl logs -f deployment/ai-assistant -n your-namespace

# You should see:
# "Successfully loaded GitHub App private key from /secrets/private-key.pem"
```

---

## Option 2: Store PEM Content as Environment Variable

If you prefer not to mount files, you can store the PEM content directly.

### Step 1: Create Secret with PEM Content

```bash
# Create secret with the PEM file content
kubectl create secret generic github-app-credentials \
  --from-literal=private-key-content="$(cat private-key.pem)" \
  --namespace=your-namespace

# Verify
kubectl get secret github-app-credentials -n your-namespace
```

### Step 2: Update Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-assistant
  namespace: your-namespace
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ai-assistant
  template:
    metadata:
      labels:
        app: ai-assistant
    spec:
      containers:
      - name: ai-assistant
        image: your-registry/ai-assistant:latest
        
        env:
        - name: GITHUB_APP_ID
          value: "2134377"
        - name: GITHUB_APP_OWNER
          value: "Cyoda-platform"
        - name: GITHUB_APP_CLIENT_ID
          value: "Iv23liau2M4692QS4yzR"
        
        # Load PEM content from secret
        - name: GITHUB_APP_PRIVATE_KEY_CONTENT
          valueFrom:
            secretKeyRef:
              name: github-app-credentials
              key: private-key-content
        
        - name: GITHUB_PUBLIC_REPO_INSTALLATION_ID
          value: "90584123"
        - name: PYTHON_PUBLIC_REPO_URL
          value: "https://github.com/Cyoda-platform/mcp-cyoda-quart-app"
        - name: JAVA_PUBLIC_REPO_URL
          value: "https://github.com/Cyoda-platform/java-client-template"
        
        ports:
        - containerPort: 8080
```

### Step 3: Apply and Verify

```bash
kubectl apply -f deployment.yaml

# Check logs - you should see:
# "Successfully loaded GitHub App private key from environment variable"
```

---

## Option 3: Use External Secrets Operator (Production)

For production environments, use **External Secrets Operator** to sync secrets from external secret managers.

### Supported Secret Managers:
- AWS Secrets Manager
- Google Secret Manager
- Azure Key Vault
- HashiCorp Vault
- And more...

### Example with AWS Secrets Manager:

#### Step 1: Store PEM in AWS Secrets Manager

```bash
aws secretsmanager create-secret \
  --name github-app-private-key \
  --secret-string file://private-key.pem \
  --region us-east-1
```

#### Step 2: Create ExternalSecret

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: github-app-secret
  namespace: your-namespace
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: github-app-private-key
    creationPolicy: Owner
  data:
  - secretKey: private-key.pem
    remoteRef:
      key: github-app-private-key
```

#### Step 3: Use in Deployment

Same as Option 1 - mount the secret as a volume.

---

## Comparison of Options

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **Option 1: Volume Mount** | ✅ Most secure<br>✅ File permissions<br>✅ Easy to rotate | ❌ Requires volume mount | **Recommended for most cases** |
| **Option 2: Env Variable** | ✅ Simple<br>✅ No volume needed | ❌ Visible in pod spec<br>❌ Less secure | Development/testing |
| **Option 3: External Secrets** | ✅ Centralized secrets<br>✅ Auto-rotation<br>✅ Audit logs | ❌ More complex setup<br>❌ External dependency | **Production environments** |

---

## Security Best Practices

### 1. Use RBAC to Restrict Secret Access

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ai-assistant
  namespace: your-namespace
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
  namespace: your-namespace
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["github-app-private-key"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-secrets
  namespace: your-namespace
subjects:
- kind: ServiceAccount
  name: ai-assistant
roleRef:
  kind: Role
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
```

### 2. Enable Encryption at Rest

```bash
# Ensure secrets are encrypted at rest in etcd
kubectl get secret github-app-private-key -n your-namespace -o yaml | \
  grep -A 1 "data:"
```

### 3. Use Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ai-assistant-network-policy
  namespace: your-namespace
spec:
  podSelector:
    matchLabels:
      app: ai-assistant
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443  # GitHub API
```

### 4. Rotate Secrets Regularly

```bash
# Update secret
kubectl create secret generic github-app-private-key \
  --from-file=private-key.pem=./new-private-key.pem \
  --namespace=your-namespace \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart deployment to pick up new secret
kubectl rollout restart deployment/ai-assistant -n your-namespace
```

---

## Complete Example: Production Deployment

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-assistant
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ai-assistant
  namespace: ai-assistant
---
apiVersion: v1
kind: Secret
metadata:
  name: github-app-private-key
  namespace: ai-assistant
type: Opaque
data:
  private-key.pem: <base64-encoded-pem-content>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-assistant
  namespace: ai-assistant
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-assistant
  template:
    metadata:
      labels:
        app: ai-assistant
    spec:
      serviceAccountName: ai-assistant
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: ai-assistant
        image: your-registry/ai-assistant:latest
        imagePullPolicy: Always
        
        env:
        - name: GITHUB_APP_ID
          value: "2134377"
        - name: GITHUB_APP_PRIVATE_KEY_PATH
          value: "/secrets/private-key.pem"
        - name: GITHUB_PUBLIC_REPO_INSTALLATION_ID
          value: "90584123"
        
        volumeMounts:
        - name: github-app-key
          mountPath: "/secrets"
          readOnly: true
        
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      
      volumes:
      - name: github-app-key
        secret:
          secretName: github-app-private-key
          defaultMode: 0440
---
apiVersion: v1
kind: Service
metadata:
  name: ai-assistant
  namespace: ai-assistant
spec:
  selector:
    app: ai-assistant
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP
```

---

## Troubleshooting

### Issue: "Private key not found"

**Check if secret exists:**
```bash
kubectl get secret github-app-private-key -n your-namespace
```

**Check if volume is mounted:**
```bash
kubectl exec -it deployment/ai-assistant -n your-namespace -- ls -la /secrets/
```

### Issue: "Permission denied"

**Check file permissions:**
```bash
kubectl exec -it deployment/ai-assistant -n your-namespace -- ls -la /secrets/private-key.pem
```

**Should show:** `-r--r----- 1 root root` (mode 0440)

**If you see permission denied errors:**
- Ensure `defaultMode: 0440` is set in the secret volume (not 0400)
- The container runs as non-root user (UID 1000) with fsGroup 1000
- Mode 0440 allows the group to read the file

### Issue: "Invalid private key"

**Verify secret content:**
```bash
kubectl get secret github-app-private-key -n your-namespace -o jsonpath='{.data.private-key\.pem}' | base64 -d | head -1
```

**Should show:** `-----BEGIN RSA PRIVATE KEY-----`

---

## Summary

✅ **Recommended Approach:** Option 1 (Volume Mount)  
✅ **Use Kubernetes Secrets**, not ConfigMaps  
✅ **Set proper file permissions** (0400)  
✅ **Enable RBAC** to restrict access  
✅ **Rotate secrets regularly**  
✅ **Use External Secrets Operator** for production  

**Your GitHub App private key is now securely deployed in Kubernetes!** 🚀


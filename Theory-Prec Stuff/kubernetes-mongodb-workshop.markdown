# Hands-On Workshop: Deploying MongoDB and Mongo Express in Kubernetes with DevOps Practices

## Overview
This workshop guides beginner to intermediate DevOps practitioners through deploying MongoDB (a NoSQL database) and Mongo Express (a web-based admin UI) in Kubernetes, emphasizing DevOps practices like automation, scalability, and security. You'll use Kubernetes resources (Deployments, Services, ConfigMaps, Secrets) and DevOps workflows to set up a production-like environment, verify it, and explore advanced topics like CI/CD and troubleshooting. By the end, you'll have a functional MongoDB stack and hands-on experience with Kubernetes in a DevOps context.

**Prerequisites:**
- Basic Docker/Kubernetes knowledge (pods, containers, `kubectl`).
- A Kubernetes cluster (e.g., Minikube, Kind, or a cloud provider like GKE/EKS/AKS).
- `kubectl` installed and configured to access your cluster.
- Text editor (e.g., VS Code, nano).
- Optional: Git for version control.

**Time Estimate:** 45-60 minutes.  
**Tools:** Kubernetes cluster, `kubectl`, browser for Mongo Express UI.

---

## 1. Theory: MongoDB, Mongo Express, and Kubernetes in DevOps

### MongoDB and Mongo Express
- **MongoDB**: A NoSQL database storing data in JSON-like documents, ideal for flexible, scalable applications. In DevOps, it's often containerized for portability.
- **Mongo Express**: A lightweight web UI for managing MongoDB, similar to phpMyAdmin for MySQL. It connects to MongoDB via a URL and credentials.

### Kubernetes Resources in DevOps Context
- **Deployments**: Manage pods (MongoDB/Mongo Express containers) with replicas for high availability and rolling updates for zero-downtime deployments.
- **Services**: Enable networking. Use `ClusterIP` for internal MongoDB access (secure, private) and `NodePort` or `LoadBalancer` for external Mongo Express UI access.
- **ConfigMaps**: Store non-sensitive configs (e.g., Mongo Express's MongoDB URL) to decouple settings from code, supporting DevOps configuration management.
- **Secrets**: Securely store sensitive data (e.g., MongoDB credentials) to align with DevOps security practices.
- **DevOps Focus**: Automation (YAML manifests), scalability (replicas), security (RBAC, Secrets), and observability (logs, status checks).

---

## 2. Hands-On: Deploying MongoDB and Mongo Express

### Step 1: Set Up Your Environment
1. Ensure your Kubernetes cluster is running:
   ```bash
   kubectl cluster-info
   ```
   - For Minikube: `minikube start`. For Kind: `kind create cluster`.

2. Create a directory for YAML manifests:
   ```bash
   mkdir k8s-mongodb-workshop
   cd k8s-mongodb-workshop
   ```

### Step 2: Create MongoDB Secret
Secrets securely store MongoDB credentials.

1. Create `mongodb-secret.yaml`:
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: mongodb-secret
   type: Opaque
   data:
     mongodb-username: YWRtaW4=  # echo -n 'admin' | base64
     mongodb-password: cGFzc3dvcmQ=  # echo -n 'password' | base64
   ```
   - Base64-encoded values for simplicity. In production, use `kubectl create secret` or secret management tools.

2. Apply:
   ```bash
   kubectl apply -f mongodb-secret.yaml
   ```

3. Verify:
   ```bash
   kubectl get secret mongodb-secret
   ```

### Step 3: Deploy MongoDB (Deployment and Service)
1. Create `mongodb-deployment.yaml`:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: mongodb
   spec:
     replicas: 1  # Single replica for simplicity; scale later
     selector:
       matchLabels:
         app: mongodb
     template:
       metadata:
         labels:
           app: mongodb
       spec:
         containers:
         - name: mongodb
           image: mongo:6.0
           env:
           - name: MONGO_INITDB_ROOT_USERNAME
             valueFrom:
               secretKeyRef:
                 name: mongodb-secret
                 key: mongodb-username
           - name: MONGO_INITDB_ROOT_PASSWORD
             valueFrom:
               secretKeyRef:
                 name: mongodb-secret
                 key: mongodb-password
           ports:
           - containerPort: 27017
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: mongodb-service
   spec:
     selector:
       app: mongodb
     ports:
     - protocol: TCP
       port: 27017
       targetPort: 27017
     type: ClusterIP  # Internal access only
   ```

2. Apply:
   ```bash
   kubectl apply -f mongodb-deployment.yaml
   ```

3. Verify:
   ```bash
   kubectl get pods -l app=mongodb
   kubectl get svc mongodb-service
   ```

### Step 4: Create Mongo Express ConfigMap
Store Mongo Express connection settings.

1. Create `mongo-express-configmap.yaml`:
   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: mongo-express-config
   data:
     ME_CONFIG_MONGODB_SERVER: mongodb-service
     ME_CONFIG_MONGODB_ENABLE_ADMIN: "true"
   ```

2. Apply:
   ```bash
   kubectl apply -f mongo-express-configmap.yaml
   ```

3. Verify:
   ```bash
   kubectl get configmap mongo-express-config
   ```

### Step 5: Deploy Mongo Express (Deployment and Service)
1. Create `mongo-express-deployment.yaml`:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: mongo-express
   spec:
     replicas: 1
     selector:
       matchLabels:
         app: mongo-express
     template:
       metadata:
         labels:
           app: mongo-express
       spec:
         containers:
         - name: mongo-express
           image: mongo-express:1.0.2
           env:
           - name: ME_CONFIG_MONGODB_ADMINUSERNAME
             valueFrom:
               secretKeyRef:
                 name: mongodb-secret
                 key: mongodb-username
           - name: ME_CONFIG_MONGODB_ADMINPASSWORD
             valueFrom:
               secretKeyRef:
                 name: mongodb-secret
                 key: mongodb-password
           - name: ME_CONFIG_MONGODB_SERVER
             valueFrom:
               configMapKeyRef:
                 name: mongo-express-config
                 key: ME_CONFIG_MONGODB_SERVER
           - name: ME_CONFIG_MONGODB_ENABLE_ADMIN
             valueFrom:
               configMapKeyRef:
                 name: mongo-express-config
                 key: ME_CONFIG_MONGODB_ENABLE_ADMIN
           ports:
           - containerPort: 8081
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: mongo-express-service
   spec:
     selector:
       app: mongo-express
     ports:
     - protocol: TCP
       port: 8081
       targetPort: 8081
       nodePort: 30001  # Optional: Adjust if needed
     type: NodePort  # Use LoadBalancer for cloud clusters
   ```

2. Apply:
   ```bash
   kubectl apply -f mongo-express-deployment.yaml
   ```

3. Verify:
   ```bash
   kubectl get pods -l app=mongo-express
   kubectl get svc mongo-express-service
   ```

### Step 6: Access Mongo Express UI
1. For Minikube:
   ```bash
   minikube service mongo-express-service --url
   ```
   - Open the URL in a browser (e.g., http://192.168.49.2:30001).
   - Log in with username `admin`, password `password`.

2. For cloud clusters (LoadBalancer):
   ```bash
   kubectl get svc mongo-express-service -o wide
   ```
   - Use the external IP and port (e.g., http://<external-ip>:8081).

3. Verify: You should see the Mongo Express UI. Create a test database or collection to confirm MongoDB connectivity.

### Step 7: Cleanup (Optional)
Remove all resources:
```bash
kubectl delete -f mongodb-secret.yaml -f mongodb-deployment.yaml -f mongo-express-configmap.yaml -f mongo-express-deployment.yaml
```

---

## 3. Advanced DevOps Topics

### CI/CD Integration
- **GitOps**: Store YAML manifests in a Git repo. Use ArgoCD or Flux to sync changes to the cluster automatically.
- **Pipeline Example**: In Jenkins/GitHub Actions:
  1. Commit YAML changes.
  2. Run `kubectl apply -f .` in a pipeline stage.
  3. Add tests (e.g., `curl` Mongo Express URL to verify).

### Security
- **RBAC**: Restrict access with a Role:
  ```yaml
  apiVersion: rbac.authorization.k8s.io/v1
  kind: Role
  metadata:
    namespace: default
    name: mongo-access
  rules:
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps", "secrets"]
    verbs: ["get", "list", "create", "update", "delete"]
  ```
  - Bind to a service account for deployments.

- **Network Policies**: Limit MongoDB access to Mongo Express only:
  ```yaml
  apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  metadata:
    name: mongodb-access
  spec:
    podSelector:
      matchLabels:
        app: mongodb
    policyTypes:
    - Ingress
    ingress:
    - from:
      - podSelector:
          matchLabels:
            app: mongo-express
      ports:
      - protocol: TCP
        port: 27017
  ```

### Troubleshooting
- **Pod Issues**: Check logs: `kubectl logs -l app=mongodb`.
- **Service Issues**: Verify endpoints: `kubectl describe svc mongodb-service`.
- **Connectivity**: Test MongoDB: `kubectl exec -it <mongodb-pod> -- mongosh -u admin -p password`.
- **Debug**: Use `kubectl describe` and `kubectl get events` for detailed status.

---

## 4. Exercises for Scaling and Configuration

1. **Scale MongoDB**:
   - Edit `mongodb-deployment.yaml`, set `replicas: 2`.
   - Apply: `kubectl apply -f mongodb-deployment.yaml`.
   - Verify: `kubectl get pods -l app=mongodb` (should see 2 pods).
   - Note: MongoDB replicas need a ReplicaSet setup for production—research this!

2. **Update Mongo Express Config**:
   - Add to `mongo-express-configmap.yaml`:
     ```yaml
     ME_CONFIG_BASICAUTH_USERNAME: admin-ui
     ```
   - Update `mongo-express-deployment.yaml` to include this env var.
   - Re-apply both. Verify: Mongo Express now requires UI login.

3. **Simulate Failure**:
   - Delete a MongoDB pod: `kubectl delete pod -l app=mongodb`.
   - Check if Deployment recreates it: `kubectl get pods -l app=mongodb`.
   - Discuss: Why did it recover? (Deployment controller!)

4. **CI/CD Practice**:
   - Create a Git repo, push YAMLs.
   - Write a GitHub Action to apply manifests on push (hint: use `kubectl` action).

---

## Wrap-Up
You've deployed a MongoDB stack in Kubernetes, automated with DevOps practices! You used Deployments for scalability, Services for networking, ConfigMaps/Secrets for configuration, and explored CI/CD and security. Experiment with scaling, tweak configs, or add monitoring (e.g., Prometheus) to level up. Keep these manifests in Git for real DevOps workflows!
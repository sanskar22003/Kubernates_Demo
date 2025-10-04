# End-to-End Kubernetes Practical Guide: Levels 2 and 3

This guide consolidates Levels 2 and 3 of the Docker and Kubernetes workshop series, building on the enhanced Python Flask web app created in previous levels. It focuses on intermediate and advanced Kubernetes concepts, including load handling, scaling, replica management, and rollbacks, all demonstrated locally using Minikube. No external hosting is required, though an optional cloud deployment step is included. Troubleshooting steps address common issues like dependency conflicts, Minikube setup, and load testing tool installation, ensuring a smooth experience for beginners.

**Prerequisites:**
- Python 3.8+ installed.
- Docker Desktop installed and running.
- Minikube and kubectl installed (installation steps provided).
- A code editor (e.g., VS Code).
- Basic terminal access (Command Prompt/PowerShell on Windows, Terminal on macOS).
- Internet for initial setups (e.g., downloading Minikube, Go for Hey).
- Time: 120-150 minutes per level, with hands-on breaks.

## Key Kubernetes Concepts and Terminology (Applies to Both Levels)
Understanding these concepts is crucial for real-world Kubernetes usage, such as scaling apps like e-commerce platforms during peak traffic:

- **Pod**: The smallest unit in Kubernetes, running one or more containers. *Analogy*: A single worker in a factory.
- **Deployment**: Manages pods, ensuring the desired number run, handling updates/rollbacks. *Analogy*: A shift manager hiring/firing workers.
- **ReplicaSet**: Ensures the correct number of pod replicas, created by a Deployment. *Analogy*: A roster keeping worker count stable.
- **Service**: Exposes pods to the network, balancing traffic across them. *Analogy*: A front desk directing customers to workers.
- **Horizontal Pod Autoscaler (HPA)**: Scales pods based on metrics like CPU. *Analogy*: Auto-hiring workers during rush hour.
- **Ingress**: Routes external HTTP/S traffic to Services. *Analogy*: A traffic cop directing cars to the factory entrance.
- **Probes (Liveness/Readiness)**: Health checks. Liveness restarts unhealthy pods; Readiness ensures traffic goes to ready pods. *Analogy*: Doctor checkups skipping sick workers.
- **Rollback**: Reverts a Deployment to a previous version. *Analogy*: Undoing a bad phone software update.

**Real-World Use**: Kubernetes ensures apps scale (e.g., Netflix during a new release), self-heal (restart crashed servers), and update without downtime.

---

## Level 2: Intermediate Scaling and Deployment

### 1. Start with Enhanced Dummy Project (app.py and requirements.txt)
Create a folder named `hello-app` and add these files (generated via LLM in Level 2):

#### app.py
```python
# Import necessary modules: Flask for web app, datetime for time, random for latency simulation, logging for logs.
from flask import Flask, jsonify
import datetime
import random
import time
import logging

# Set up logging: This helps debug by printing info to console.
logging.basicConfig(level=logging.INFO)

# Create the app instance.
app = Flask(__name__)

# Global counter for requests: Simple metric to track total requests.
request_count = 0

# Function to simulate latency: Adds a random delay (0-2 seconds) to mimic real-world slowdowns.
def simulate_latency():
    delay = random.uniform(0, 2)  # Random delay in seconds.
    time.sleep(delay)
    logging.info(f"Simulated latency: {delay} seconds")

# Root endpoint: Serves a simple message.
@app.route('/')
def hello_world():
    global request_count
    request_count += 1
    simulate_latency()  # Add delay for realism.
    logging.info("Handled / request")
    return 'Hello World from our enhanced workshop!'

# /time endpoint: Returns current server time in JSON.
@app.route('/time')
def get_time():
    global request_count
    request_count += 1
    simulate_latency()
    logging.info("Handled /time request")
    current_time = datetime.datetime.now().isoformat()
    return jsonify({'time': current_time})

# /metrics endpoint: Exposes basic stats like request count.
@app.route('/metrics')
def metrics():
    global request_count
    logging.info("Handled /metrics request")
    return jsonify({'request_count': request_count})

# Run the app: Starts the server.
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

#### requirements.txt
```
Flask==3.0.3
```

### 2. Locally Run the App
**Steps:**
1. Navigate to `hello-app`: `cd hello-app`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run: `python app.py`.
4. Test: Open browser to `http://localhost:5000/`, `/time`, `/metrics`.

**Troubleshooting:**
- **Requirements Version Conflict**:
  - If `pip install` fails due to dependency conflicts:
    1. Create a virtual environment: `python -m venv venv`.
    2. Activate:
       - Windows: `venv\Scripts\activate`.
       - macOS: `source venv/bin/activate`.
    3. Re-install: `pip install -r requirements.txt`.
- **app.py Not Running Inside Venv**:
  - If Python path issues:
    1. Deactivate: `deactivate`.
    2. Run with explicit path: `C:\Users\sansk\AppData\Local\Programs\Python\Python312\python.exe app.py` (adjust to your Python installation path).
    3. Verify Python version: `python --version` (ensure 3.8+). Reinstall Python if needed from python.org.
  - If still fails: Check for syntax errors in `app.py` (e.g., copy-paste issues). Compare with the code above.

### 3. Containerizing in Docker, Build, Run
Create `Dockerfile` in `hello-app`:

```dockerfile
# Base image with Python.
FROM python:3.9-slim

# Working dir.
WORKDIR /app

# Copy and install deps.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code.
COPY app.py .

# Expose port.
EXPOSE 5000

# Run command.
CMD ["python", "app.py"]
```

**Steps:**
1. Build: `docker build -t enhanced-app:latest .`.
2. Run: `docker run -p 5000:5000 enhanced-app:latest`.
3. Test: Browser to `http://localhost:5000/`, `/time`, `/metrics`.

### 4. Docker Push
**Steps:**
1. Create a free Docker Hub account at hub.docker.com.
2. Login: `docker login` (enter credentials).
3. Tag: `docker tag enhanced-app:latest yourusername/enhanced-app:latest`.
4. Push: `docker push yourusername/enhanced-app:latest`.

### 5. Setting Up a Kubernetes Environment Using Minikube
**Why Minikube?** It's a free, local Kubernetes cluster, beginner-friendly, and stable across Windows/macOS. Alternatives like K3d are lighter but may have networking issues (as you experienced), making Minikube a reliable choice.

**Installation Steps (If Not Installed):**
- **Windows:**
  1. Download Minikube from https://minikube.sigs.k8s.io/docs/start/ (select Windows AMD64).
  2. Run the `.exe` installer, follow prompts.
  3. Enable Hyper-V (needed for Minikube):
     - Settings → Apps → Programs and Features → Turn Windows features on/off → Check Hyper-V → Restart.
  4. Verify: `minikube version`.
  5. If fails: Ensure Docker Desktop is running; restart computer if Hyper-V was just enabled.
- **macOS:**
  1. Install via Homebrew: `brew install minikube`.
  2. If no Homebrew: Install from https://minikube.sigs.k8s.io/docs/start/ (macOS AMD64 or ARM64).
  3. Verify: `minikube version`.
  4. If fails: Ensure Docker Desktop is running; check Brew permissions (`brew doctor`).

**Setup Steps:**
1. Start Minikube: `minikube start` (takes 2-5 minutes).
2. Enable Addons:
   - Metrics Server: `minikube addons enable metrics-server` (enables CPU/memory monitoring for HPA).
   - Ingress: `minikube addons enable ingress` (enables HTTP routing for external access).
   - **Why needed?** Metrics Server powers autoscaling; Ingress simulates production-like HTTP traffic routing.
3. Verify: `kubectl get nodes` (shows one node, status "Ready").

### 6. Create Enhanced Manifests
Create these YAML files in `hello-app`.

#### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: enhanced-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: enhanced-app
  template:
    metadata:
      labels:
        app: enhanced-app
    spec:
      containers:
      - name: enhanced-container
        image: yourusername/enhanced-app:latest
        ports:
        - containerPort: 5000
        livenessProbe:
          httpGet:
            path: /
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /metrics
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            cpu: "100m"
          limits:
            cpu: "500m"
```

#### service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: enhanced-service
spec:
  selector:
    app: enhanced-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

#### hpa.yaml
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: enhanced-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: enhanced-deployment
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
```

### 7. Apply and Test Locally with Minikube
**Steps:**
1. Apply manifests: `kubectl apply -f deployment.yaml -f service.yaml -f hpa.yaml`.
2. Get access URL: `minikube service enhanced-service --url` (e.g., http://192.168.49.2:XXXXX).
3. Test in browser: Visit `/`, `/time`, `/metrics`.

**Troubleshooting:**
- **Image Not Loading (Error: ImagePullBackOff)**:
  - If Minikube can't pull your image:
    1. Load locally: `minikube image load enhanced-app:latest`.
    2. Verify: `minikube ssh` → `docker images` (confirm image exists) → `exit`.
    3. Re-apply: `kubectl apply -f deployment.yaml`.
  - If persists: Ensure Docker Hub image is public or credentials are set (`kubectl create secret docker-registry`).
- **Service URL Not Accessible**:
  - Run `minikube tunnel` (in a separate terminal) to assign external IPs.
  - Re-check: `kubectl get svc`.

### 8. Ingress (Optional) and Why It’s Used
**Why?** Ingress provides advanced HTTP routing (e.g., domain-based, path-based), simulating production environments with multiple services or SSL.

**Steps:**
1. Create `ingress.yaml`:
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: enhanced-ingress
   spec:
     rules:
     - http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: enhanced-service
               port:
                 number: 80
   ```
2. Apply: `kubectl apply -f ingress.yaml`.
3. Get Minikube IP: `minikube ip`.
4. Test:
   - Add to hosts file: `/etc/hosts` (Linux/macOS) or `C:\Windows\System32\drivers\etc\hosts` (Windows) → Add `<minikube-ip> example.com`.
   - Browser to http://example.com.
5. If fails: Ensure Ingress addon enabled (`minikube addons list`); check `kubectl get ingress`.

### 9. Steps to Host in Render.com (Optional Cloud Demo)
**Steps:**
1. Sign up at render.com (free tier, 512MB RAM services).
2. New → Web Service → Docker.
3. Enter your Docker Hub image: `yourusername/enhanced-app:latest`.
4. Set port to 5000, add env vars if needed (e.g., `FLASK_ENV=production`).
5. Deploy → Get subdomain (e.g., yourapp.onrender.com).
6. Test: Visit `/`, `/time`, `/metrics`.

**Troubleshooting:**
- **Deployment Fails:** Check Render logs (Dashboard → Logs) for image pull errors. Ensure image is public.
- **Port Issues:** Verify port 5000 is set in Render settings.

### 10. Simulate Real-World Usage Using Hey
**Hey Explanation:** Hey is a load-testing tool. Parameters:
- `-n`: Total requests.
- `-c`: Concurrent requests.
- `-z`: Duration (e.g., 5m for 5 minutes).
Example: `hey -n 1000 -c 50 http://localhost:5000/time` sends 1000 requests with 50 concurrent, stressing the `/time` endpoint with latency.

**Setup Hey (If Not Installed):**
- **Windows:**
  1. Download Go installer from golang.org/dl (Windows MSI).
  2. Run installer, add `C:\Go\bin` to PATH (Control Panel → System → Advanced → Environment Variables).
  3. Verify: `go version`.
  4. Install Hey: `go install github.com/rakyll/hey@latest`.
  5. If fails: Check PATH (`echo %PATH%`); reinstall Go or run `go env` to debug.
- **macOS:**
  1. Install Homebrew (if missing): `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`.
  2. Install Go: `brew install go`.
  3. Install Hey: `go install github.com/rakyll/hey@latest`.
  4. If fails: Run `brew doctor` to fix Brew issues; verify Go path (`go env GOPATH`).

**Steps:**
1. Get Service URL: `minikube service enhanced-service --url`.
2. Run Load: `hey -n 1000 -c 20 <url>/time`.
3. Observe Scaling: `kubectl get hpa --watch` (replicas increase to max=5).
4. Check Metrics: `kubectl top pods` (shows CPU usage).

**Troubleshooting:**
- **Hey Not Found:** Ensure `~/go/bin/hey` is in PATH; run with full path if needed.
- **No Scaling:** Verify metrics-server (`kubectl get pods -n kube-system | grep metrics-server`); re-enable if missing.

---

## Level 3: Advanced Simulations Locally

### 1. Enabling and Accessing the Kubernetes Dashboard
**Why?** The Dashboard visualizes pods, scaling, and metrics, making demos engaging (e.g., see replicas live).

**Steps:**
1. Enable: `minikube addons enable dashboard`.
2. Access: `minikube dashboard` (opens browser) or `--url` for link.
3. Explore: Workloads → Pods/Deployments for status; Horizontal Pod Autoscalers for scaling metrics.

**Troubleshooting (End-to-End):**
- **Addon Not Enabled:** Check: `minikube addons list | grep dashboard`. Enable if false.
- **Browser Fails to Open:** Use `--url`, copy-paste link. Try specific port: `minikube dashboard --port=8080`.
- **Blank Page/Access Denied:**
  1. Get token: `kubectl -n kubernetes-dashboard describe secret $(kubectl -n kubernetes-dashboard get secret | grep admin-user | awk '{print $1}')`.
  2. Copy token, paste in Dashboard login.
  3. If persists: Restart Minikube (`minikube stop; minikube start`).
- **Network Issues:** Ensure Minikube is running (`minikube status`); check Docker Desktop.

### 2. Deploying the Base App
**Cleanup Level 2 (Start Fresh):**
1. Delete: `kubectl delete -f hpa.yaml -f service.yaml -f deployment.yaml`.
2. Verify: `kubectl get pods,svc,deployments,hpa` (should be empty for app).
3. Modify `deployment.yaml`: Set `replicas: 1` (baseline for Level 3).
4. Re-apply: `kubectl apply -f deployment.yaml -f service.yaml -f hpa.yaml`.
5. Access: `minikube service enhanced-service --url`.
6. Dashboard: Workloads → Pods (confirm 1 running pod).

### 3. Simulating Load Handling – How Pods Handle Traffic
**Steps:**
1. Scale to 2: `kubectl scale deployment enhanced-deployment --replicas=2`.
2. Load Test: `hey -n 200 -c 10 <url>/time`.
3. Dashboard: Pods → Logs (see alternating requests); Services → enhanced-service → Endpoints (lists pod IPs).
4. Terminal: `kubectl logs -l app=enhanced-app --tail=10`.

### 4. Scaling Up and Down – Manual and Automatic
**Manual Scaling:**
1. Up: `kubectl scale deployment enhanced-deployment --replicas=4`.
2. Load Test: `hey -n 1000 -c 20 <url>/time`.
3. Down: `kubectl scale deployment enhanced-deployment --replicas=1`.
4. Dashboard: Deployments → See "Desired: 4, Current: 4", then back to 1.

**Automatic Scaling (HPA):**
1. Apply `hpa.yaml`.
2. Sustained Load: `hey -z 5m -c 20 <url>/time` (5 minutes).
3. Watch: `kubectl get hpa --watch`; Dashboard → Horizontal Pod Autoscalers → CPU graphs.

### 5. Managing Replicas – Role of ReplicaSets
**Steps:**
1. View: `kubectl get rs` (named like `enhanced-deployment-XXXXX`).
2. Delete Pod: `kubectl delete pod <pod-name>` (get name from `kubectl get pods`).
3. Watch: `kubectl get pods --watch` (new pod created).
4. Dashboard: ReplicaSets → Events (shows self-healing).

### 6. Handling Rollbacks – Updating and Reverting Deployments
**Steps:**
1. Create v2 Image:
   - Edit `app.py`: Change `hello_world()` return to `'Hello v2 from our enhanced workshop!'`.
   - Build/Push: `docker build -t yourusername/enhanced-app:v2 .; docker push yourusername/enhanced-app:v2`.
2. Update: Edit `deployment.yaml` (image: `yourusername/enhanced-app:v2`), apply.
3. Status: `kubectl rollout status deployment/enhanced-deployment`.
4. Test: Browser to URL (see "Hello v2").
5. Rollback: `kubectl rollout undo deployment/enhanced-deployment`.
6. Dashboard: Deployments → Revisions/Events (see update and rollback).

---

## Best Practices for Local Simulations
- **Environment Variables/Secrets**:
  - Add to `deployment.yaml`:
    ```yaml
    env:
    - name: MY_VAR
      valueFrom:
        secretKeyRef:
          name: my-secret
          key: value
    ```
  - Create: `kubectl create secret generic my-secret --from-literal=value='secret'`.
- **Resource Limits**: Already in `deployment.yaml`—prevents CPU overuse in Minikube.

---

## Cleanup
1. Delete Resources: `kubectl delete -f hpa.yaml -f service.yaml -f deployment.yaml -f ingress.yaml`.
2. Stop Minikube: `minikube stop`.

---

## Exercises and Challenges
1. **Basic**: During load test, delete a pod—watch self-healing in Dashboard.
2. **Intermediate**: Set HPA to 30% CPU, re-run load test, observe faster scaling.
3. **Challenge**: Create v3 with a bug (e.g., crash on `/metrics`), deploy, rollback, fix.
4. **Advanced**: Add ConfigMap for custom message, mount in Deployment, update without rebuild.

---

## Troubleshooting Summary
- **Level 2**:
  - Dependency Conflicts: Use virtualenv, explicit Python path.
  - Minikube Install: Enable Hyper-V (Windows), Homebrew (macOS).
  - Image Not Loading: Use `minikube image load`.
  - Hey Setup: Install Go, ensure PATH includes `~/go/bin`.
- **Level 3**:
  - Dashboard Issues: Use token, restart Minikube, check addon status.

---

This guide equips you to demonstrate Kubernetes' real-world power locally, with clear visuals via the Dashboard. Download and share with students for hands-on learning!
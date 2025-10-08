# Grafana and Prometheus Monitoring Workshop: End-to-End Setup on Windows

## Workshop Introduction

Welcome to this beginner-friendly workshop on **Grafana** and **Prometheus**, two powerful tools for monitoring and visualizing your Windows machine's performance. **Prometheus** collects and stores metrics (like CPU, memory, and disk usage), while **Grafana** turns them into beautiful, interactive dashboards. This guide is tailored for students with basic PowerShell knowledge but no prior experience with these tools. We'll walk you through installation, configuration, visualization, and alerting, using your verified steps and troubleshooting fixes (e.g., manual MSI installation, Grafana service issues). Think of Prometheus as a data collector and Grafana as an artist creating clear, actionable visuals.

**Why Monitor?** Monitoring is like a health check for your PC, catching issues (e.g., high CPU) before they cause crashes. This workshop ensures you can set up a live monitoring system on Windows, even if you hit errors like the Grafana service issue you faced.

## Workshop Objectives
- Install Prometheus, Windows Exporter, and Grafana on Windows.
- Configure Prometheus to scrape CPU, memory, and disk metrics.
- Build a Grafana dashboard with live visualizations.
- Set up a CPU usage alert and test it.
- Troubleshoot common issues (e.g., service start failures, port conflicts).
- Apply best practices for a clean, beginner-friendly setup.

## Prerequisites and Setup

### Hardware/Software
- Windows 10 (2004+) or 11 (64-bit, admin access).
- 4GB+ RAM, 10GB free disk space.
- Internet connection for downloads.
- Tools: PowerShell (admin), web browser (e.g., Chrome), text editor (e.g., Notepad++).

### Prerequisite Steps
1. **Open PowerShell as Admin:**
   - Right-click Start → Windows PowerShell (Admin).
   - **Expected Output:** PowerShell prompt with admin privileges.
2. **Download Tools:**
   - **Windows Exporter:** [github.com/prometheus-community/windows_exporter](https://github.com/prometheus-community/windows_exporter/releases) → `windows_exporter-0.31.3-amd64.msi`.
   - **Prometheus:** [prometheus.io/download](https://prometheus.io/download) → `prometheus-3.6.0.windows-amd64.zip`.
   - **Grafana OSS:** [grafana.com/grafana/download](https://grafana.com/grafana/download) → `grafana_12.2.0_17949786146_windows_amd64.msi`.
   - Save to `C:\Users\<YourUser>\Downloads`.
   - **Expected Output:** Files in Downloads folder.

## Section 1: Setup & Installation

### Step 1.1: Install Windows Exporter
Windows Exporter collects system metrics for Prometheus.

1. **Install MSI (Fixing Manual Issue):**
   - Your manual MSI install failed, so use PowerShell (as you did):
     ```
     Start-Process msiexec.exe -ArgumentList '/i "C:\Users\sansk\Downloads\windows_exporter-0.31.3-amd64.msi"' -Verb RunAs
     ```
     **Expected Output:** MSI installer opens, completes silently. Installs to `C:\Program Files\windows_exporter`.
2. **Start Service:**
   ```
   Start-Service windows_exporter
   Get-Service windows_exporter
   ```
   **Expected Output:**
   ```
   Status   Name               DisplayName
   ------   ----               -----------
   Running  windows_exporter   windows_exporter
   ```
3. **Allow Port 9100:**
   ```
   New-NetFirewallRule -DisplayName "Windows Exporter" -Direction Inbound -Protocol TCP -LocalPort 9100 -Action Allow
   ```
   **Expected Output:**
   ```
   Name                          : {a22d47b8-f276-4517-9127-df44dbb6c959}
   DisplayName                   : Windows Exporter
   Enabled                       : True
   Direction                     : Inbound
   Action                        : Allow
   ...
   PrimaryStatus                 : OK
   ```
4. **Test Metrics:**
   - Browser: `http://localhost:9100/metrics`
   - **Expected Output:** Text output with metrics like `windows_cpu_time_total`, `windows_memory_available_bytes`, `windows_logical_disk_free_bytes`.

### Step 1.2: Install Prometheus
Prometheus collects and stores metrics.

1. **Extract ZIP:**
   - Unzip `prometheus-3.6.0.windows-amd64.zip` to `C:\Prometheus` (use File Explorer or PowerShell):
     ```
     Expand-Archive -Path "C:\Users\sansk\Downloads\prometheus-3.6.0.windows-amd64.zip" -DestinationPath "C:\Prometheus"
     ```
     **Expected Output:** Folder `C:\Prometheus\prometheus-3.6.0.windows-amd64` created.
2. **Test Run:**
   ```
   cd C:\Prometheus\prometheus-3.6.0.windows-amd64
   .\prometheus.exe
   ```
   **Expected Output:**
   ```
   time=2025-10-07T14:26:36.193+05:30 level=INFO source=main.go:770 msg="Starting Prometheus Server" mode=server version="(version=3.6.0, ...)"
   ...
   time=2025-10-07T14:26:36.278+05:30 level=INFO source=main.go:1274 msg="Server is ready to receive web requests."
   ```
3. **Allow Port 9090:**
   ```
   New-NetFirewallRule -DisplayName "Prometheus" -Direction Inbound -Protocol TCP -LocalPort 9090 -Action Allow
   ```
   **Expected Output:** Similar to port 9100 rule, "PrimaryStatus: OK".
4. **Test UI:** Browser: `http://localhost:9090`
   - **Expected Output:** Prometheus web UI loads with status and graph pages.

### Step 1.3: Install Grafana
Grafana visualizes Prometheus data.

1. **Install MSI (Fixing Manual Issue):**
   ```
   Start-Process msiexec.exe -ArgumentList '/i "C:\Users\sansk\Downloads\grafana_12.2.0_17949786146_windows_amd64.msi"' -Verb RunAs
   ```
   **Expected Output:** MSI installs to `C:\Program Files\GrafanaLabs\grafana`.
2. **Start Service (Fixing Your Error):**
   - Your `Get-Service grafana` showed "Stopped". Install as service:
     ```
     cd "C:\Program Files\GrafanaLabs\grafana\bin"
     .\grafana-server.exe --install
     Start-Service grafana
     Get-Service grafana
     ```
     **Expected Output:**
     ```
     Status   Name               DisplayName
     ------   ----               -----------
     Running  grafana            grafana
     ```
   - If manual start fails (as in your log):
     - Stop any running process:
       ```
       netstat -ano | findstr :3000
       taskkill /PID 13420 /F
       ```
       **Expected Output:**
       ```
       TCP    0.0.0.0:3000           0.0.0.0:0              LISTENING       13420
       SUCCESS: The process with PID 13420 has been terminated.
       ```
     - Restart: `Start-Service grafana`.
3. **Allow Port 3000:**
   ```
   New-NetFirewallRule -DisplayName "Grafana" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow
   ```
   **Expected Output:**
   ```
   Name                          : {077fa0f0-e091-429f-8576-a9279d24c4a1}
   DisplayName                   : Grafana
   Enabled                       : True
   Direction                     : Inbound
   Action                        : Allow
   ...
   PrimaryStatus                 : OK
   ```
4. **Test UI:** Browser: `http://localhost:3000` (login: admin/admin, change password).
   - **Expected Output:** Grafana login page, then dashboard.

## Section 2: Prometheus Configuration

Configure Prometheus to scrape Windows Exporter metrics.

1. **Edit prometheus.yml:**
   - Open `C:\Prometheus\prometheus-3.6.0.windows-amd64\prometheus.yml` in Notepad.
   - Replace with:
     ```yaml
     global:
       scrape_interval: 15s
     scrape_configs:
       - job_name: 'windows'
         static_configs:
           - targets: ['localhost:9100']
     ```
     **Expected Output:** File saved.
2. **Restart Prometheus:**
   - Stop (Ctrl+C if running), then:
     ```
     .\prometheus.exe
     ```
     **Expected Output:** Logs show "Completed loading of configuration file" and scraping `localhost:9100`.
3. **Verify Metrics:**
   - Browser: `http://localhost:9090/graph`
   - Query: `windows_cpu_time_total`, `windows_memory_available_bytes`, `windows_logical_disk_free_bytes`
   - **Expected Output:** Graphs show CPU time, memory (bytes), disk free space (bytes).

**Hands-On:** Query `rate(windows_cpu_time_total[5m])` in Prometheus UI. See CPU trend.

## Section 3: Grafana Configuration

Connect Grafana to Prometheus and create a dashboard.

1. **Add Data Source:**
   - Log into `http://localhost:3000`.
   - Menu → Connections → Data Sources → Add new → Prometheus.
   - URL: `http://localhost:9090` → Save & Test.
   - **Expected Output:** "Data source is working".
2. **Create Dashboard:**
   - Menu → Dashboards → New → New Dashboard.
   - Add panels:
     - **Line Graph (CPU):**
       - Query: `rate(windows_cpu_time_total[5m]) * 100`
       - Title: "CPU Usage (%)"
       - Visualization: Time Series
       - **Expected Output:** Graph shows CPU % over time.
     - **Gauge (Memory):**
       - Query: `(windows_memory_available_bytes / windows_memory_total_bytes) * 100`
       - Title: "Memory Available (%)"
       - Visualization: Gauge
       - **Expected Output:** Gauge shows % memory available.
     - **Table (Disk):**
       - Query: `windows_logical_disk_free_bytes`
       - Title: "Disk Free Space (Bytes)"
       - Visualization: Table
       - **Expected Output:** Table lists free space per drive.
   - Set auto-refresh: Settings → Auto-refresh → 5s.
   - Save as "Windows System Monitor".
   - **Expected Output:** Dashboard updates live.

## Section 4: Alerts

Set a CPU usage alert.

1. **Create Alert:**
   - In CPU panel, Edit → Alert → New alert rule.
   - Condition: `rate(windows_cpu_time_total[5m]) * 100 > 80`
   - Name: "High CPU Usage"
   - Evaluation: Every 1m, for 1m.
   - Notification: Default (UI alert).
   - Save.
   - **Expected Output:** Alert rule saved.
2. **Test:** (See Section 5).

## Section 5: Hands-On Demo

Simulate load to see live updates and alerts.

1. **Stress System:**
   - Open apps (e.g., Chrome with 10 tabs, VS Code).
   - Optional: Install `stress` in WSL (`sudo apt install stress`, then `stress --cpu 2`).
2. **Observe Dashboard:**
   - Refresh `http://localhost:3000` → Windows System Monitor.
   - **Expected Output:** CPU graph spikes, memory gauge drops, disk table updates.
3. **Trigger Alert:**
   - If CPU > 80%, check Alerts tab.
   - **Expected Output:** Red "High CPU Usage" alert in UI.

**Hands-On:** Add a panel for `windows_os_processes`. Observe changes during load.

## Section 6: Troubleshooting

- **Windows Exporter Not Running:**
  - `Get-Service windows_exporter` → Restart: `Restart-Service windows_exporter`.
  - MSI failed? Re-run: `Start-Process msiexec.exe -ArgumentList '/i ...' -Verb RunAs`.
- **Prometheus Not Scraping:**
  - Check `http://localhost:9100/metrics`.
  - Verify `prometheus.yml` syntax.
  - Firewall: Re-run port 9100/9090 rules.
- **Grafana Service Stopped (Your Issue):**
  - Check `Get-Service grafana`. If stopped:
    - Stop conflicting process: `netstat -ano | findstr :3000`, `taskkill /PID <PID> /F`.
    - Re-install service: `.\grafana-server.exe --install`, `Start-Service grafana`.
  - Logs: `C:\Program Files\GrafanaLabs\grafana\data\log\grafana.log`.
- **No Metrics in Grafana:**
  - Verify Prometheus URL (`http://localhost:9090`).
  - Check query syntax (e.g., `rate()` needs [5m]).
- **Port Conflicts:**
  - `netstat -ano | findstr :3000` → Kill conflicting PIDs.
  - Re-run firewall rules.

## Section 7: Best Practices & Closing

- **Best Practices:**
  - Monitor only key metrics (CPU, memory, disk) initially.
  - Use clear panel titles and organize dashboards.
  - Secure Grafana: Change admin password, enable HTTPS.
  - Backup `prometheus.yml` and Grafana dashboards (export JSON).
  - Update tools via official sites.
- **Closing:** You've set up a live monitoring system! Prometheus and Grafana now track your Windows performance. Experiment with metrics like `windows_net_bytes_total` or add email alerts. Visit [grafana.com/docs](https://grafana.com/docs) and [prometheus.io/docs](https://prometheus.io/docs). What's your next monitoring project? Share in class!
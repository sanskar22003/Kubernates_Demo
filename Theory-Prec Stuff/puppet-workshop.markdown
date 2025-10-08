# Puppet Workshop: Hands-On Demo on Windows Laptop

## Overview
This beginner-friendly Puppet workshop demonstrates configuration management by setting up a Puppet Master and Puppet Agent on two Ubuntu VMs running in VirtualBox on your Windows laptop. The goal is to apply a simple manifest that creates `/tmp/hello-puppet.txt` with "Hello, Puppet World!" on the agent. This revised version addresses previous issues (e.g., networking, SSH, certificates, permissions) to ensure a smooth ~60-minute lab.

**Objectives:**
- Install VirtualBox and create two Ubuntu VMs.
- Configure Puppet Server (Master) and Agent.
- Apply a manifest and verify results.
- Troubleshoot common issues proactively.

**Prerequisites:**
- Windows laptop with admin access.
- Internet access for VirtualBox and Ubuntu cloud image.
- 8GB RAM (2GB per VM) and 30GB disk space.
- Basic command-line knowledge (PowerShell).
- **Time:** ~60 minutes.

**Engagement Tips:**
- Test each step (e.g., SSH, services) to catch issues early.
- Show the file creation live for instant feedback.
- If stuck, skip to Step 7 (file creation) for a quick win.

## Step 1: Install VirtualBox on Windows Laptop (5-10 minutes)
1. **Download VirtualBox:**
   - Visit [virtualbox.org](https://www.virtualbox.org/wiki/Downloads).
   - Download VirtualBox 7.x for Windows (EXE) and Extension Pack (`.vbox-extpack`).
   - Save to `C:\Users\<YourUser>\Downloads`.

2. **Install VirtualBox:**
   - Run the EXE as admin (right-click → Run as administrator).
   - Accept defaults; allow network adapters.
   - Verify: Open VirtualBox via Start menu (search "VirtualBox").

3. **Install Extension Pack:**
   - In VirtualBox: File → Preferences → Extensions → Plus icon → Select `.vbox-extpack` → Install.
   - Purpose: Enhances networking.

4. **Disable Hyper-V (Fix Conflicts):**
   - Open PowerShell as admin:
     ```
     bcdedit /set hypervisorlaunchtype off
     ```
   - Reboot if prompted.

**Troubleshooting:**
- **Hyper-V Error:** If VirtualBox fails, confirm Hyper-V is disabled (re-run command and reboot).
- **Admin Issues:** Ensure you have admin rights.

## Step 2: Create Two Ubuntu VMs (15-20 minutes)
Use Ubuntu 20.04 cloud image (no ISO needed).

### Step 2.1: Download Ubuntu Cloud Image
- Download: [https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.ova](https://cloud-images.ubuntu.com/focal/current/focal-server-cloudimg-amd64.ova) (~600MB).
- Save to `C:\Users\<YourUser>\Downloads`.

### Step 2.2: Create Puppet Master VM
1. **Import OVA:**
   - In VirtualBox: File → Import Appliance → Select `.ova`.
   - Settings:
     - Name: `puppet-master`
     - CPU: 1
     - RAM: 2048 MB
     - Disk: Default (~10GB)
     - Network: Bridged Adapter (select Wi-Fi/Ethernet adapter).
   - Import (1-2 minutes).

2. **Create Seed ISO for Login (Fix Password Issue):**
   - Open PowerShell:
     ```
     wsl
     ```
   - Install cloud-utils:
     ```
     sudo apt update
     sudo apt install cloud-utils -y
     ```
   - Create directory:
     ```
     mkdir ~/cloud-init
     cd ~/cloud-init
     ```
   - Create `user-data`:
     ```
     cat <<EOF > user-data
     #cloud-config
     users:
       - name: ubuntu
         sudo: ALL=(ALL) NOPASSWD:ALL
         groups: sudo
         shell: /bin/bash
         lock_passwd: false
         plain_text_passwd: 'puppet123'
     EOF
     ```
   - Create `meta-data`:
     ```
     echo "instance-id: puppet-master" > meta-data
     ```
   - Generate ISO:
     ```
     cloud-localds seed.iso user-data meta-data
     ```
   - Copy to Windows:
     ```
     cp seed.iso /mnt/c/Users/<YourUser>/Downloads/
     ```
   - Exit WSL: `exit`.

3. **Attach Seed ISO:**
   - In VirtualBox, select `puppet-master` → Settings → Storage → Controller: IDE → Empty → Click disk icon → Choose a disk file → Select `seed.iso` → OK.
   - Purpose: Sets `ubuntu` user with password `puppet123`.

4. **Start VM and Configure:**
   - Start `puppet-master` (normal mode for visibility).
   - Log in (user: `ubuntu`, password: `puppet123`).
   - Install SSH:
     ```
     sudo apt update
     sudo apt install openssh-server -y
     sudo systemctl enable ssh
     sudo systemctl start ssh
     ```
   - Get IP:
     ```
     ip addr show
     ```
     - If no IP for `enp0s3`:
       ```
       sudo ip link set enp0s3 up
       sudo dhclient -v enp0s3
       ip addr show
       ```
     - Note IP (e.g., `192.168.1.101`).
   - Test from PowerShell:
     ```
     ssh ubuntu@<master-ip>
     ```

**Troubleshooting:**
- **No IP:** Re-run `sudo dhclient -v enp0s3`. Check Bridged Adapter.
- **SSH Fails:** Run `sudo ufw allow 22` in VM; check Windows Firewall.

### Step 2.3: Create Puppet Agent VM
1. **Clone VM (Fix No Clone Option):**
   - Power off `puppet-master`.
   - In PowerShell:
     ```
     cd "C:\Program Files\Oracle\VirtualBox"
     .\VBoxManage.exe list vms
     .\VBoxManage.exe clonevm puppet-master --name puppet-agent --register --mode all
     ```
   - Verify: In VirtualBox, see `puppet-agent`.

2. **Configure Network:**
   - Settings → Network → Adapter 1 → Bridged Adapter.

3. **Start and Setup:**
   - Start `puppet-agent`.
   - Log in (`ubuntu`, `puppet123`).
   - Install SSH and get IP (repeat Step 2.2.4).
   - Note IP (e.g., `192.168.1.102`).

**Troubleshooting:**
- **Clone Fails:** Ensure `puppet-master` is off. Check VirtualBox path.
- **IP Issues:** Same as above.

## Step 3: Set Up SSH Key-Based Authentication (5 minutes)
1. **Generate Key:**
   - In PowerShell:
     ```
     ssh-keygen -t ed25519 -C "puppet-key"
     ```
     - Accept defaults, no passphrase.
   - Verify:
     ```
     dir $HOME\.ssh
     cat $HOME\.ssh\id_ed25519.pub
     ```

2. **Copy Key (Manual Fix for `ssh-copy-id`):**
   - For Master:
     - Copy public key: `cat $HOME\.ssh\id_ed25519.pub`.
     - SSH to VM: `ssh ubuntu@<master-ip>`.
     - Add key:
       ```
       mkdir -p ~/.ssh
       chmod 700 ~/.ssh
       nano ~/.ssh/authorized_keys
       ```
       - Paste key, save, exit.
       ```
       chmod 600 ~/.ssh/authorized_keys
       ```
     - Exit: `exit`.
   - Repeat for Agent.

3. **Test SSH:**
   - `ssh ubuntu@<master-ip>` (no password).
   - `ssh ubuntu@<agent-ip>`.

**Troubleshooting:**
- **SSH Fails:** Verify key in `~/.ssh/authorized_keys`. Check port 22: `sudo netstat -tuln | grep 22`.

## Step 4: Install Puppet Server on Master VM (10 minutes)
1. **SSH to Master:**
   - `ssh ubuntu@<master-ip>`

2. **Update System:**
   ```
   sudo apt update && sudo apt upgrade -y
   ```

3. **Install Repository:**
   ```
   wget https://apt.puppet.com/puppet7-release-focal.deb
   sudo dpkg -i puppet7-release-focal.deb
   sudo apt update
   ```

4. **Install Puppet Server:**
   ```
   sudo apt install puppetserver -y
   ```

5. **Configure JVM:**
   ```
   sudo nano /etc/default/puppetserver
   ```
   - Set: `JAVA_ARGS="-Xms512m -Xmx512m"`

6. **Set Hostname:**
   ```
   sudo hostnamectl set-hostname puppetmaster
   sudo nano /etc/hosts
   ```
   - Add:
     ```
     127.0.0.1 localhost
     127.0.0.1 puppetmaster
     <master-ip> puppetmaster puppet
     ```
   - Reboot: `sudo reboot`.

7. **Clear SSH Key (Fix Hostname Verification):**
   - In PowerShell (after reboot):
     ```
     ssh-keygen -R <master-ip>
     ssh ubuntu@<master-ip>
     ```

8. **Start Service:**
   ```
   sudo systemctl enable puppetserver
   sudo systemctl start puppetserver
   sudo systemctl status puppetserver
   ```
   - If fails:
     ```
     sudo netstat -tuln | grep 8140
     sudo systemctl restart puppetserver
     ```

**Troubleshooting:**
- **Service Fails:** Check logs: `sudo tail /var/log/puppetlabs/puppetserver/puppetserver.log`.
- **Port 8140:** Ensure open: `sudo ufw allow 8140`.

## Step 5: Install Puppet Agent on Agent VM (5 minutes)
1. **SSH to Agent:**
   - `ssh ubuntu@<agent-ip>`

2. **Update and Install Repo:**
   - Repeat Step 4.2-4.3.

3. **Install Agent:**
   ```
   sudo apt install puppet-agent -y
   ```

4. **Set Hostname:**
   ```
   sudo hostnamectl set-hostname puppetagent
   sudo nano /etc/hosts
   ```
   - Add:
     ```
     127.0.0.1 localhost
     127.0.0.1 puppetagent
     <agent-ip> puppetagent
     <master-ip> puppetmaster puppet
     ```
   - Disable cloud-init:
     ```
     sudo touch /etc/cloud/cloud-init.disabled
     sudo cloud-init clean --logs
     sudo rm -rf /var/lib/cloud/*
     ```
   - Reboot: `sudo reboot`.

5. **Clear SSH Key:**
   - In PowerShell:
     ```
     ssh-keygen -R <agent-ip>
     ssh ubuntu@<agent-ip>
     ```

6. **Configure Puppet:**
   ```
   sudo nano /etc/puppetlabs/puppet/puppet.conf
   ```
   - Add:
     ```
     [main]
     server = puppetmaster
     certname = puppetagent
     ```

7. **Start Service:**
   ```
   sudo systemctl enable puppet
   sudo systemctl start puppet
   ```

**Troubleshooting:**
- **Cloud-Init Interference:** Verify removal: `ls /var/lib/cloud`.

## Step 6: Create Manifest on Master (5 minutes)
1. **On Master:**
   ```
   sudo nano /etc/puppetlabs/code/environments/production/manifests/site.pp
   ```
   - Add:
     ```puppet
     node default {
       file { '/tmp/hello-puppet.txt':
         ensure  => present,
         content => "Hello, Puppet World!\n",
       }
     }
     ```

2. **Validate:**
   ```
   sudo /opt/puppetlabs/bin/puppet parser validate /etc/puppetlabs/code/environments/production/manifests/site.pp
   ```

## Step 7: Connect and Apply Configuration (10 minutes)
1. **On Agent:**
   ```
   sudo /opt/puppetlabs/bin/puppet agent -t
   ```
   - Expect certificate error.

2. **On Master (Fix Certificate Issues):**
   - Clean old certificates:
     ```
     sudo /opt/puppetlabs/bin/puppetserver ca clean --certname puppetagent
     sudo rm -rf /etc/puppetlabs/puppet/ssl/*
     ```
   - Generate CA:
     ```
     sudo /opt/puppetlabs/bin/puppetserver ca setup --subject-alt-names puppetmaster,puppet
     ```
   - List certificates:
     ```
     sudo /opt/puppetlabs/bin/puppetserver ca list
     ```
   - Sign:
     ```
     sudo /opt/puppetlabs/bin/puppetserver ca sign --certname puppetagent
     ```

3. **On Agent (Manual CA Copy):**
   - If certificate errors persist:
     - On Master: `sudo cat /etc/puppetlabs/puppetserver/ca/ca_crt.pem`.
     - On Agent:
       ```
       sudo mkdir -p /etc/puppetlabs/puppet/ssl/certs
       sudo nano /etc/puppetlabs/puppet/ssl/certs/ca.pem
       ```
       - Paste CA content, save.
       ```
       sudo chown puppet:puppet /etc/puppetlabs/puppet/ssl/certs/ca.pem
       sudo chmod 644 /etc/puppetlabs/puppet/ssl/certs/ca.pem
       ```
   - Run agent:
     ```
     sudo /opt/puppetlabs/bin/puppet agent -t --server puppetmaster --certname puppetagent
     ```

4. **Verify:**
   ```
   cat /tmp/hello-puppet.txt
   ```
   - Output: "Hello, Puppet World!"

**Troubleshooting:**
- **Certificate Errors:** Repeat clean/setup/sign. Check permissions: `sudo ls -l /etc/puppetlabs/puppet/ssl`.
- **Connection Fails:** Verify port 8140: `sudo netstat -tuln | grep 8140`.

## Step 8: Test and Explore (5 minutes)
- Re-run agent: `sudo /opt/puppetlabs/bin/puppet agent -t` (idempotent).
- Edit manifest (e.g., change content), re-run, show changes.
- Demo: Project file creation to class.

## Step 9: Cleanup (Optional, 5 minutes)
- Stop services:
  - Master: `sudo systemctl stop puppetserver`
  - Agent: `sudo systemctl stop puppet`
- Purge: `sudo apt purge puppetserver puppet-agent -y`
- Delete VMs: In VirtualBox, right-click → Remove → Delete all files.

## Final Configuration Files
### Master: `/etc/hosts`
```
127.0.0.1 localhost
127.0.0.1 puppetmaster
<master-ip> puppetmaster puppet
```

### Master: `/etc/puppetlabs/puppet/puppet.conf`
```
[server]
vardir = /opt/puppetlabs/server/data/puppetserver
logdir = /var/log/puppetlabs/puppetserver
rundir = /var/run/puppetlabs/puppetserver
pidfile = /var/run/puppetlabs/puppetserver/puppetserver.pid
codedir = /etc/puppetlabs/code
[main]
server = puppetmaster
certname = puppetmaster
```

### Agent: `/etc/hosts`
```
127.0.0.1 localhost
127.0.0.1 puppetagent
<agent-ip> puppetagent
<master-ip> puppetmaster puppet
```

### Agent: `/etc/puppetlabs/puppet/puppet.conf`
```
[main]
server = puppetmaster
certname = puppetagent
```

## Puppet Manifest
```puppet
node default {
  file { '/tmp/hello-puppet.txt':
    ensure  => present,
    content => "Hello, Puppet World!\n",
  }
}
```
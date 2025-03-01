# Raspberry Pi Monitoring Setup

This guide will help you set up a monitoring system for your Raspberry Pi. The system will track CPU temperature, CPU usage, memory usage, and disk usage. It will automatically shut down the Raspberry Pi if the temperature exceeds a defined threshold and send email alerts for high CPU, memory, or disk usage.

### Features:
- **Monitor system temperature, CPU usage, memory usage, and disk usage.**
- **Shutdown Raspberry Pi if the temperature exceeds a defined threshold.**
- **Send email alerts for high CPU, memory, or disk usage.**
- **Logging to track the system's health.**
- **Runs every 5 minutes using `systemd` timer.**

---

## Prerequisites

Before proceeding, ensure you have the following:

- A Raspberry Pi running Raspbian or another compatible OS.
- Python 3 and the required libraries installed.
- A working email account (e.g., Gmail) to send email alerts.
- Basic familiarity with the command line.
- Git installed.

---

## Step 1: Install Required Packages

To install Git, Python 3, and the necessary Python libraries:

```bash
sudo apt update
sudo apt install python3-pip git
pip3 install psutil
```

---

## Step 2: Clone the Repository

Clone the project from the GitHub repository:

```bash
git clone https://github.com/kevin4hrens/pi-monitoring.git
cd pi-monitoring
```

This will download the project files, including the monitoring script (`monitor.py`).

---

## Step 3: Prepare the Python Script

1. The Python script for monitoring is located in the `pi-monitoring/monitor.py` file. This script will handle system resource monitoring and email alerts.

---

## Step 4: Set Up Environment Variables

You need to create a `.env` file to store your sensitive data, such as email credentials.
Inside the repository, you will find a .env.dist file. This file contains example environment variable values.

1. **Create the `.env` file inside the project folder**:

```bash
nano /home/pi/pi-monitoring/.env
```

2. **Add the following environment variables** to the `.env file:

```bash
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_email_password
RECEIVER_EMAIL=receiver_email@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
TEMP_THRESHOLD=80
CPU_THRESHOLD=90
MEMORY_THRESHOLD=90
DISK_THRESHOLD=90
LOG_FILE=/home/pi/pi-monitoring/monitoring.log
```

Make sure to replace the placeholders with your actual values.

---

## Step 5: Create Systemd Service and Timer

1. **Create the systemd service**:

```bash
sudo nano /etc/systemd/system/monitoring.service
```

2. **Add the following content** to the `monitoring.service` file:

```ini
[Unit]
Description=Raspberry Pi Monitoring Service
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /home/pi/pi-monitoring/monitor.py
WorkingDirectory=/home/pi/pi-monitoring
EnvironmentFile=/home/pi/pi-monitoring/.env
StandardOutput=append:/home/pi/pi-monitoring/monitoring.log
StandardError=append:/home/pi/pi-monitoring/monitoring.log
User=pi
Group=pi

[Install]
WantedBy=multi-user.target
```

3. **Create the systemd timer**:

```bash
sudo nano /etc/systemd/system/monitoring.timer
```

4. **Add the following content** to the `monitoring.timer` file:

```ini
[Unit]
Description=Run monitoring every 5 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
Unit=monitoring.service

[Install]
WantedBy=timers.target
```

---

## Step 6: Enable and Start the Service and Timer

1. **Reload systemd**:

```bash
sudo systemctl daemon-reload
```

2. **Enable and start the service and timer**:

```bash
sudo systemctl enable monitoring.service
sudo systemctl enable monitoring.timer
```

3. **Start the timer**:

```bash
sudo systemctl start monitoring.timer
```

4. **Check the status** of the timer:

```bash
sudo systemctl status monitoring.timer
```

---

## Step 7: Test the Monitoring System

You can manually test the script to ensure everything is working correctly by running:

```bash
sudo systemctl start monitoring.service
```

Check the logs for activity in `/home/pi/pi-monitoring/monitoring.log`:

```bash
tail -f /home/pi/pi-monitoring/monitoring.log
```

You should see entries about the system's temperature, CPU usage, memory usage, and disk usage.

---

## Logrotation

```bash
sudo apt install logrotate -y

sudo nano /etc/logrotate.d/pi-monitoring

```

```ini
/home/pi/pi-monitoring/monitoring.log {
    daily                # Rotate logs daily
    rotate 7             # Keep 7 days of logs
    compress             # Compress old log files
    missingok            # Don't throw an error if the log file is missing
    notifempty           # Don't rotate if the log file is empty
    create 0644 pi pi    # Create a new log file with the specified permissions after rotation
    size 10M             # Rotate the log file when it reaches 10MB
    dateext              # Add a date extension to rotated files (e.g. monitoring.log-2023-02-15.gz)
    maxage 7             # Delete rotated log files older than 7 days
}
```

---

## Troubleshooting

- If the emails aren't sending, ensure that your email credentials are correct and that your SMTP server settings match your email provider's configuration.
- Check the logs (`/home/pi/pi-monitoring/monitoring.log`) for any error messages related to system resource usage or script issues.

---

## Conclusion

You now have a fully automated monitoring system for your Raspberry Pi that checks key system parameters (temperature, CPU, memory, and disk) every 5 minutes, and will send email alerts or shut down the system if necessary. The systemd timer ensures that the script runs periodically without needing to worry about manual execution.

---

This guide assumes that the monitoring script `monitor.py` is located inside the `/home/pi/pi-monitoring/` directory and is referenced in the systemd service configuration.

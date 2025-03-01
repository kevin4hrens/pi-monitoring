import os
import psutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from dotenv import load_dotenv

load_dotenv()

# Load environment variables
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")  # Default to Gmail
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # Default to port 587
TEMP_THRESHOLD = float(os.getenv("TEMP_THRESHOLD", 80))
CPU_THRESHOLD = float(os.getenv("CPU_THRESHOLD", 90))
MEMORY_THRESHOLD = float(os.getenv("MEMORY_THRESHOLD", 90))
DISK_THRESHOLD = float(os.getenv("DISK_THRESHOLD", 90))

# Configure logging
DIRECTORY = os.getenv("DIRECTORY")

LOG_FILE="{}/{}".format(DIRECTORY, "monitoring.log")

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

# Function to get CPU temperature
def get_cpu_temp():
    try:
        temp = float(open("/sys/class/thermal/thermal_zone0/temp").read()) / 1000
        return temp
    except Exception as e:
        logging.error(f"Error reading temperature: {e}")
        return None

# Function to monitor system health
def monitor_system():
    temp = get_cpu_temp()
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent

    logging.info(f"Temperature: {temp}°C")
    logging.info(f"CPU Usage: {cpu_usage}%")
    logging.info(f"Memory Usage: {memory_usage}%")
    logging.info(f"Disk Usage: {disk_usage}%")

    # Check if temperature is high, shut down and send email
    if temp and temp >= TEMP_THRESHOLD:
        shutdown_system("Temperature too high!")
    # Check other metrics and send email alerts
    elif cpu_usage >= CPU_THRESHOLD:
        send_email("High CPU Usage Alert", f"CPU usage is too high! Current usage: {cpu_usage}%")
    elif memory_usage >= MEMORY_THRESHOLD:
        send_email("High Memory Usage Alert", f"Memory usage is too high! Current usage: {memory_usage}%")
    elif disk_usage >= DISK_THRESHOLD:
        send_email("High Disk Usage Alert", f"Disk usage is too high! Current usage: {disk_usage}%")

# Function to send an email alert
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, text)
        server.quit()
        logging.info("Alert email sent!")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

# Function to shutdown the system and send an email
def shutdown_system(reason):
    logging.error(f"Shutting down due to: {reason}")
    send_email("Raspberry Pi Shutdown Alert", f"Your Raspberry Pi is shutting down because: {reason}")
    os.system("sudo shutdown now")

# Run monitoring once (triggered by systemd timer)
monitor_system()

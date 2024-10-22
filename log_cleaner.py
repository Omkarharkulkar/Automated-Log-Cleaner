#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import shutil
import time
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

# Function to clean up log files based on age and size
def clean_logs(log_dir, max_age_days, max_size_mb):
    current_time = time.time()
    deleted_files = []

    # Iterate through all files in the specified log directory
    for root, dirs, files in os.walk(log_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_stat = os.stat(file_path)
            
            # Check if the file is older than max_age_days
            file_age = (current_time - file_stat.st_mtime) / (60 * 60 * 24)  # Convert to days
            file_size_mb = file_stat.st_size / (1024 * 1024)  # Convert size to MB

            if file_age > max_age_days or file_size_mb > max_size_mb:
                try:
                    os.remove(file_path)  # Delete the file
                    deleted_files.append(file_path)
                    print(f"Deleted: {file_path} (Age: {file_age:.2f} days, Size: {file_size_mb:.2f} MB)")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

    return deleted_files

# Function to generate a log report of deleted files
def generate_report(deleted_files):
    if not deleted_files:
        print("No files were deleted.")
        return None

    # Create a timestamp for the report
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_name = f"log_cleanup_report_{timestamp}.txt"
    
    # Write the report
    with open(report_name, 'w') as report_file:
        report_file.write("Log Cleanup Report\n")
        report_file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        report_file.write("Deleted Files:\n")
        for file in deleted_files:
            report_file.write(f"{file}\n")
    
    print(f"Cleanup report saved as: {report_name}")
    return report_name

# Function to send an email report
def send_email_report(report_file, recipient_email):
    sender = "youremail@example.com"
    recipient = recipient_email
    subject = "Log Cleanup Report"
    
    with open(report_file, 'r') as f:
        report_content = f.read()

    msg = MIMEText(report_content)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    try:
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login(sender, "your_password")
            server.sendmail(sender, recipient, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Main function
def main():
    log_dir = "/var/log/"  # Directory where logs are stored
    max_age_days = 30  # Define the maximum age of logs to keep (in days)
    max_size_mb = 100  # Define the maximum file size in MB

    # Clean logs and generate a report
    deleted_files = clean_logs(log_dir, max_age_days, max_size_mb)
    report_file = generate_report(deleted_files)

    # If a report was generated, send it via email
    if report_file:
        recipient_email = "recipient@example.com"  # Change this to the recipient's email
        send_email_report(report_file, recipient_email)

if __name__ == "__main__":
    main()


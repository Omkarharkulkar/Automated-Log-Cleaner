import os
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext

# Function to clean up log files based on age and size
def clean_logs(log_dir, max_age_days, max_size_mb):
    current_time = time.time()
    deleted_files = []
    messages = []

    # Iterate through all files in the specified log directory
    for root, dirs, files in os.walk(log_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_stat = os.stat(file_path)

            file_age = (current_time - file_stat.st_mtime) / (60 * 60 * 24)  # Convert to days
            file_size_mb = file_stat.st_size / (1024 * 1024)  # Convert size to MB

            if file_age > max_age_days or file_size_mb > max_size_mb:
                try:
                    os.remove(file_path)  # Attempt to delete the file
                    deleted_files.append(file_path)
                    messages.append(f"Deleted: {file_path} (Age: {file_age:.2f} days, Size: {file_size_mb:.2f} MB)")
                except PermissionError:
                    messages.append(f"Permission denied: {file_path}. Try running as Administrator.")
                except FileNotFoundError:
                    messages.append(f"File not found: {file_path}. It may have been deleted already.")
                except Exception as e:
                    messages.append(f"Error deleting {file_path}: {e}")

    return deleted_files, messages

# Function to generate a log report of deleted files
def generate_report(deleted_files):
    if not deleted_files:
        return None

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_name = f"log_cleanup_report_{timestamp}.txt"

    with open(report_name, 'w') as report_file:
        report_file.write("Log Cleanup Report\n")
        report_file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        report_file.write("Deleted Files:\n")
        for file in deleted_files:
            report_file.write(f"{file}\n")

    return report_name

# Function to send an email report
def send_email_report(report_file, recipient_email):
    sender = "abc@gmail.com"
    subject = "Log Cleanup Report"
    
    with open(report_file, 'r') as f:
        report_content = f.read()

    msg = MIMEText(report_content)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login(sender, "ABC@112")
            server.sendmail(sender, recipient_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# Function to handle log cleanup process
def start_cleanup():
    log_dir = log_dir_entry.get().strip()
    recipient_email = recipient_email_entry.get().strip()

    if not log_dir or not recipient_email:
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return
    
    try:
        max_age_days = int(max_age_entry.get())
        max_size_mb = int(max_size_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values for age and size.")
        return

    # Clean logs and generate a report
    deleted_files, messages = clean_logs(log_dir, max_age_days, max_size_mb)

    # Update the output text area with messages
    output_text.delete(1.0, tk.END)  # Clear previous text
    for message in messages:
        output_text.insert(tk.END, message + '\n')

    # If a report was generated, send it
    if deleted_files:
        report_file = generate_report(deleted_files)
        if report_file:
            if send_email_report(report_file, recipient_email):
                messagebox.showinfo("Success", "Log cleanup and email report sent successfully!")
            else:
                messagebox.showerror("Email Error", "Failed to send email report.")
    else:
        output_text.insert(tk.END, "No files were deleted.\n")

# Function to select log directory
def select_log_dir():
    dir_path = filedialog.askdirectory()
    log_dir_entry.delete(0, tk.END)
    log_dir_entry.insert(0, dir_path)

# Set up the GUI
root = tk.Tk()
root.title("Log Cleanup Tool")

# Log Directory
tk.Label(root, text="Log Directory:").grid(row=0, column=0, padx=10, pady=10)
log_dir_entry = tk.Entry(root, width=50)
log_dir_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=select_log_dir).grid(row=0, column=2, padx=10, pady=10)

# Max Age
tk.Label(root, text="Max Age (days):").grid(row=1, column=0, padx=10, pady=10)
max_age_entry = tk.Entry(root)
max_age_entry.grid(row=1, column=1, padx=10, pady=10)

# Max Size
tk.Label(root, text="Max Size (MB):").grid(row=2, column=0, padx=10, pady=10)
max_size_entry = tk.Entry(root)
max_size_entry.grid(row=2, column=1, padx=10, pady=10)

# Recipient Email
tk.Label(root, text="Recipient Email:").grid(row=3, column=0, padx=10, pady=10)
recipient_email_entry = tk.Entry(root)
recipient_email_entry.grid(row=3, column=1, padx=10, pady=10)

# Start Cleanup Button
tk.Button(root, text="Start Cleanup", command=start_cleanup).grid(row=4, column=1, pady=20)

# Output Text Area
tk.Label(root, text="Output:").grid(row=5, column=0, padx=10, pady=10)
output_text = scrolledtext.ScrolledText(root, width=60, height=15)
output_text.grid(row=5, column=1, columnspan=2, padx=10, pady=10)

# Run the GUI event loop
root.mainloop()

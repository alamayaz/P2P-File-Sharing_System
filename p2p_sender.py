import socket
import os
import time
from tkinter import Tk, filedialog, messagebox, Label, Button, Entry, StringVar, Frame, Toplevel
from tkinter.ttk import Progressbar, Style, Treeview, Scrollbar
import json
import threading
from datetime import datetime

# Globals for Pause/Resume and History
paused = False
stop_transfer = False  # Added to handle stopping transfers
file_paths = []
sent_files_history = []
transfer_thread = None


def browse_files():
    global file_paths
    file_paths = filedialog.askopenfilenames()
    lbl_file_count.config(text=f"Selected: {len(file_paths)} file(s)" if file_paths else "No file selected.")


def send_files():
    global transfer_thread
    if not file_paths:
        messagebox.showerror("Error", "Please select files to send.")
        return

    receiver_ip = entry_ip.get()
    receiver_port = entry_port.get()
    auth_password = entry_password.get()

    if not receiver_ip or not receiver_port or not auth_password:
        messagebox.showerror("Error", "Please fill in all fields (IP, Port, Password).")
        return

    try:
        receiver_port = int(receiver_port)
        # Start the file transfer in a separate thread
        transfer_thread = threading.Thread(
            target=file_transfer_process,
            args=(receiver_ip, receiver_port, auth_password)
        )
        transfer_thread.daemon = True
        transfer_thread.start()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send file: {e}")


def file_transfer_process(receiver_ip, receiver_port, auth_password):
    global paused, stop_transfer
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((receiver_ip, receiver_port))
            s.send(auth_password.encode())  # Send authentication password
            auth_response = s.recv(1024).decode()
            if auth_response != "AUTH_SUCCESS":
                messagebox.showerror("Error", "Authentication failed.")
                return

            for file_path in file_paths:
                if stop_transfer:
                    lbl_status.config(text="Status: Transfer Stopped")
                    return

                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                s.send(json.dumps({"filename": filename, "size": file_size}).encode())
                s.recv(1024)  # Wait for ACK

                with open(file_path, "rb") as f:
                    sent = 0
                    start_time = time.time()  # Start timer

                    while sent < file_size:
                        if stop_transfer:
                            lbl_status.config(text="Status: Transfer Stopped")
                            return

                        if paused:
                            lbl_status.config(text="Status: Paused")
                            while paused:
                                time.sleep(0.1)
                            lbl_status.config(text="Status: Transferring")

                        chunk = f.read(65536)  # 64KB chunks
                        if not chunk:
                            break
                        s.send(chunk)
                        sent += len(chunk)

                        # Calculate progress, speed, and time remaining
                        progress = int((sent / file_size) * 100)
                        progress_var.set(progress)
                        progress_bar.update()

                        elapsed_time = time.time() - start_time
                        if elapsed_time > 0:
                            speed = sent / elapsed_time  # Speed in bytes/second

                            if speed >= 1024 * 1024:
                                lbl_speed.config(text=f"Speed: {speed / (1024 * 1024):.2f} MB/s")
                            else:
                                lbl_speed.config(text=f"Speed: {speed / 1024:.2f} KB/s")

                            time_remaining = (file_size - sent) / speed if speed > 0 else 0
                            lbl_time.config(text=f"Time Remaining: {time_remaining:.2f} seconds")

                # Add to history
                sent_files_history.append({
                    "filename": filename,
                    "size": file_size,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                messagebox.showinfo("Success", f"File '{filename}' sent successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send file: {e}")


def pause_transfer():
    global paused
    paused = True


def resume_transfer():
    global paused
    paused = False


def stop_file_transfer():
    global stop_transfer
    stop_transfer = True


def show_history():
    # Create a new window for the history
    history_window = Toplevel(app)
    history_window.title("File Transfer History")
    history_window.geometry("600x400")

    # Create the Treeview widget (table)
    tree = Treeview(history_window, columns=("filename", "time", "size"), show="headings", height=15)
    tree.heading("filename", text="File Name")
    tree.heading("time", text="Time")
    tree.heading("size", text="Size")
    tree.column("filename", width=250)
    tree.column("time", width=200)
    tree.column("size", width=100)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Add scrollbar for the table
    scrollbar = Scrollbar(history_window, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    # Populate the table with history data
    for file_info in sent_files_history:
        tree.insert("", "end", values=(file_info['filename'], file_info['time'], f"{file_info['size']} bytes"))


# GUI for the sender
app = Tk()
app.title("File Sender - Dashboard Layout")
app.geometry("700x500")

# Style configuration
style = Style()
style.theme_use("clam")
style.configure("TButton", font=("Arial", 12))
style.configure("TLabel", font=("Arial", 12))

# Layout Frames
header_frame = Frame(app, height=60, bg="#1e1e1e")
header_frame.pack(fill="x")

sidebar_frame = Frame(app, width=150, bg="#2e2e2e")
sidebar_frame.pack(side="left", fill="y")

main_frame = Frame(app, bg="#ffffff")
main_frame.pack(side="left", fill="both", expand=True)

# Header Section
Label(header_frame, text="File Sender", bg="#1e1e1e", fg="white", font=("Arial", 16, "bold")).pack(side="left", padx=20, pady=10)

# Sidebar Section
Button(sidebar_frame, text="Select Files", command=browse_files, font=("Arial", 12), bg="#3e3e3e", fg="white").pack(pady=10, padx=10, fill="x")
Button(sidebar_frame, text="Send Files", command=send_files, font=("Arial", 12), bg="#3e3e3e", fg="white").pack(pady=10, padx=10, fill="x")
Button(sidebar_frame, text="Pause Transfer", command=pause_transfer, font=("Arial", 12), bg="#3e3e3e", fg="white").pack(pady=10, padx=10, fill="x")
Button(sidebar_frame, text="Resume Transfer", command=resume_transfer, font=("Arial", 12), bg="#3e3e3e", fg="white").pack(pady=10, padx=10, fill="x")
Button(sidebar_frame, text="Stop Transfer", command=stop_file_transfer, font=("Arial", 12), bg="#3e3e3e", fg="white").pack(pady=10, padx=10, fill="x")
Button(sidebar_frame, text="History", command=show_history, font=("Arial", 12), bg="#3e3e3e", fg="white").pack(pady=10, padx=10, fill="x")

# Main Content Area
Label(main_frame, text="File Transfer Details", font=("Arial", 14), bg="#ffffff").pack(pady=10)

lbl_file_count = Label(main_frame, text="No file selected.", font=("Arial", 12), bg="#ffffff")
lbl_file_count.pack(pady=5)

Label(main_frame, text="Receiver IP:", bg="#ffffff").pack(pady=5)
entry_ip = Entry(main_frame, font=("Arial", 12), width=30)
entry_ip.pack(pady=5)

Label(main_frame, text="Receiver Port:", bg="#ffffff").pack(pady=5)
entry_port = Entry(main_frame, font=("Arial", 12), width=30)
entry_port.pack(pady=5)

Label(main_frame, text="Authentication Password:", bg="#ffffff").pack(pady=5)
entry_password = Entry(main_frame, show="*", font=("Arial", 12), width=30)
entry_password.pack(pady=5)

progress_var = StringVar()
progress_bar = Progressbar(main_frame, orient="horizontal", length=400, mode="determinate", variable=progress_var)
progress_bar.pack(pady=10)

lbl_speed = Label(main_frame, text="Speed: 0 KB/s", bg="#ffffff")
lbl_speed.pack(pady=5)

lbl_time = Label(main_frame, text="Time Remaining: 0 seconds", bg="#ffffff")
lbl_time.pack(pady=5)

lbl_status = Label(main_frame, text="Status: Ready", font=("Arial", 12, "italic"), bg="#ffffff")
lbl_status.pack(pady=10)

app.mainloop()
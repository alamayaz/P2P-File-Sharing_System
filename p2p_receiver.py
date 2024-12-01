import socket
from tkinter import Tk, Label, filedialog, Button, StringVar, Frame, Toplevel
from tkinter.ttk import Progressbar, Style, Treeview, Scrollbar
import os
import time
import json
import threading
from datetime import datetime

# Globals for Save Path, Pause, Resume, and History
save_path = os.getcwd()
auth_password = "default_password"  # Predefined password for authentication
received_files_history = []
paused = False
stop_transfer = False  # To stop the transfer
transfer_thread = None

def start_server():
    global transfer_thread
    transfer_thread = threading.Thread(target=run_server)
    transfer_thread.daemon = True
    transfer_thread.start()

def run_server():
    global save_path
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", 5000))  # Bind to any IP on port 5000
            s.listen(5)
            lbl_status.config(text="Waiting for connection...")
            while True:
                conn, addr = s.accept()
                lbl_status.config(text=f"Connected to {addr}")
                threading.Thread(target=handle_client, args=(conn, addr)).start()
    except Exception as e:
        lbl_status.config(text=f"Error: {e}")

def handle_client(conn, addr):
    global received_files_history, paused, stop_transfer
    try:
        # Authentication
        password = conn.recv(1024).decode().strip()
        if password != auth_password:
            conn.send("AUTH_FAILED".encode())
            lbl_status.config(text=f"Authentication failed from {addr}.")
            conn.close()
            return
        conn.send("AUTH_SUCCESS".encode())

        while True:
            # Receive file metadata
            metadata = conn.recv(1024).decode()
            if not metadata:
                break

            metadata = json.loads(metadata)
            filename = metadata["filename"]
            file_size = metadata["size"]

            file_path = os.path.join(save_path, filename)
            conn.send("ACK".encode())  # Send ACK

            # Receive file data
            received = 0
            start_time = time.time()  # Start timer
            with open(file_path, "wb") as f:
                while received < file_size:
                    if stop_transfer:
                        lbl_status.config(text="Status: Transfer Stopped")
                        conn.close()
                        return

                    if paused:
                        lbl_status.config(text="Status: Paused")
                        while paused:
                            time.sleep(0.1)
                        lbl_status.config(text="Status: Receiving")

                    chunk = conn.recv(65536)  # 64KB chunks
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)

                    # Update progress and speed
                    progress = int((received / file_size) * 100)
                    progress_var.set(progress)
                    progress_bar.update()

                    elapsed_time = time.time() - start_time
                    if elapsed_time > 0:
                        speed = received / elapsed_time  # Speed in bytes/second
                        if speed >= 1024 * 1024:
                            lbl_speed.config(text=f"Speed: {speed / (1024 * 1024):.2f} MB/s")
                        else:
                            lbl_speed.config(text=f"Speed: {speed / 1024:.2f} KB/s")

                        time_remaining = (file_size - received) / speed if speed > 0 else 0
                        lbl_time.config(text=f"Time Remaining: {time_remaining:.2f} seconds")

            # Log transfer to history
            received_files_history.append({
                "filename": filename,
                "size": file_size,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            lbl_status.config(text=f"File received: {filename}")
    except Exception as e:
        lbl_status.config(text=f"Error: {e}")
    finally:
        conn.close()

def set_save_directory():
    global save_path
    save_path = filedialog.askdirectory()
    if save_path:
        lbl_dir.config(text=f"Save Directory: {save_path}")
    else:
        lbl_dir.config(text="No directory selected.")

def pause_transfer():
    global paused
    paused = True

def resume_transfer():
    global paused
    paused = False

def stop_transfer_func():
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
    for file_info in received_files_history:
        tree.insert("", "end", values=(file_info['filename'], file_info['time'], f"{file_info['size']} bytes"))

# GUI for the receiver
app = Tk()
app.title("File Receiver - Dashboard Layout")
app.geometry("800x600")

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
Label(header_frame, text="File Receiver", bg="#1e1e1e", fg="white", font=("Arial", 16, "bold")).pack(side="left", padx=20, pady=10)

# Sidebar Section
Button(sidebar_frame, text="Set Save Directory", command=set_save_directory, font=("Arial", 12), bg="#3e3e3e", fg="white").pack(pady=10, padx=10, fill="x")
Button(sidebar_frame, text="Start Receiving", command=start_server, font=("Arial", 12), bg="#3e3e3e", fg="white").pack(pady=10, padx=10, fill="x")
Button(sidebar_frame, text="Pause Transfer", command=pause_transfer, font=("Arial", 12), bg="#3e3e3e", fg="white").pack(pady=10, padx=10, fill="x")
Button(sidebar_frame, text="Resume Transfer", command=resume_transfer, font=("Arial", 12), bg="#3e3e3e", fg="white").pack(pady=10, padx=10, fill="x")
Button(sidebar_frame, text="Stop Transfer", command=stop_transfer_func, font=("Arial", 12), bg="#3e3e3e", fg="white").pack(pady=10, padx=10, fill="x")
Button(sidebar_frame, text="History", command=show_history, font=("Arial", 12), bg="#3e3e3e", fg="white").pack(pady=10, padx=10, fill="x")

# Main Content Area
Label(main_frame, text="File Receiving Details", font=("Arial", 14), bg="#ffffff").pack(pady=10)

lbl_dir = Label(main_frame, text=f"Save Directory: {save_path}", font=("Arial", 12), bg="#ffffff")
lbl_dir.pack(pady=5)

progress_var = StringVar()
progress_bar = Progressbar(main_frame, orient="horizontal", length=400, mode="determinate", variable=progress_var)
progress_bar.pack(pady=10)

lbl_speed = Label(main_frame, text="Speed: 0 KB/s", bg="#ffffff")
lbl_speed.pack(pady=5)

lbl_time = Label(main_frame, text="Time Remaining: 0 seconds", bg="#ffffff")
lbl_time.pack(pady=5)

lbl_status = Label(main_frame, text="Status: Not connected.", font=("Arial", 12, "italic"), bg="#ffffff")
lbl_status.pack(pady=10)

app.mainloop()
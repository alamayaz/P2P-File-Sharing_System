Based on the analysis of the provided Python scripts (`p2p_receiver.py` and `p2p_sender.py`), here is a suggested `README.md` for your GitHub repository:

---

# Peer-to-Peer File Sharing System

This repository implements a peer-to-peer (P2P) file sharing system using socket programming in Python. It includes two components:
- **File Sender**: Allows the user to select and send files to a receiver.
- **File Receiver**: Receives files from a sender and saves them to a specified directory.

The system includes a graphical user interface (GUI) for both sender and receiver, making it user-friendly and intuitive.

---

## Features

### General
- **GUI-based operation** using Tkinter.
- **Authentication**: Ensures secure file transfers with password protection.
- **Pause, Resume, and Stop Controls**: Flexible file transfer management.
- **Transfer History**: Logs file transfers for future reference.

### Sender
- **File Selection**: Allows users to select multiple files for transfer.
- **Progress Tracking**: Displays file transfer progress, speed, and estimated time remaining.
- **File History**: Logs sent files with details such as filename, size, and timestamp.

### Receiver
- **Save Directory Selection**: Users can specify where to save received files.
- **Transfer Progress**: Tracks the progress, speed, and estimated time for incoming files.
- **History Management**: Logs received files for reference.

---

## Requirements

### Dependencies
The system requires Python 3.x and the following libraries:
- `socket`
- `os`
- `time`
- `json`
- `threading`
- `datetime`
- `tkinter`
- `ttk`

You can install any missing libraries using `pip`:
```bash
pip install tkinter
```

---

## Usage

### Running the Receiver
1. Open the terminal and run:
   ```bash
   python p2p_receiver.py
   ```
2. Use the GUI to:
   - Set the save directory.
   - Start the server to begin listening for file transfers.
   - Pause, resume, or stop the file transfer as needed.
   - View transfer history.

### Running the Sender
1. Open the terminal and run:
   ```bash
   python p2p_sender.py
   ```
2. Use the GUI to:
   - Select files to send.
   - Provide the receiver's IP, port, and authentication password.
   - Monitor the transfer progress.
   - Pause, resume, or stop the transfer as needed.
   - View transfer history.

---

## Authentication

The sender and receiver use a predefined password (`default_password` in the receiver code). Ensure that both sender and receiver use the same password for successful authentication. You can change the default password by editing the `auth_password` variable in both scripts.

---

## Notes

- **Transfer Interruptions**: Transfers can be paused, resumed, or stopped at any time using the provided controls.
- **Transfer Speed**: The system dynamically calculates and displays the transfer speed in real-time.
- **Compatibility**: Ensure that the sender and receiver are running on the same network or have the necessary network configurations for connectivity.

---

## Screenshots


![WhatsApp Image 2024-11-17 at 10 37 03 PM](https://github.com/user-attachments/assets/db6a5d1e-e964-4e13-bb2a-430943ad6b0a)


![WhatsApp Image 2024-11-17 at 10 38 17 PM](https://github.com/user-attachments/assets/47a504b4-e80a-4931-a321-6896df78b445)


---

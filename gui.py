import tkinter as tk
from tkinter import filedialog, messagebox
from downloader import download_content
import threading
from tkinter.ttk import Progressbar
import json

class DownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("URL Content Downloader")
        self.root.geometry("500x400")
        
        self.is_paused = False
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.is_downloading = False
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the GUI elements."""
        tk.Label(self.root, text="Enter URL:").pack(pady=5)
        
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.pack(pady=5)
        
        self.download_button = tk.Button(self.root, text="Download", command=self.start_download)
        self.download_button.pack(pady=20)

        self.progress_bar = Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.speed_label = tk.Label(self.root, text="Download Speed: 0 KB/s")
        self.speed_label.pack(pady=5)

        self.time_remaining_label = tk.Label(self.root, text="Time Remaining: 0s")
        self.time_remaining_label.pack(pady=5)
        
        self.history_button = tk.Button(self.root, text="Download History", command=self.show_history)
        self.history_button.pack(pady=10)

        # Log Text Widget
        self.log_text = tk.Text(self.root, height=10, width=50, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(pady=10)
        
        # Pause/Resume Button
        self.pause_button = tk.Button(self.root, text="Pause", command=self.toggle_pause, state=tk.DISABLED)
        self.pause_button.pack(pady=5)

    def update_log(self, message: str):
        """Update the log text widget with new messages."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.yview(tk.END)

    def start_download(self):
        """Start the download process in a separate thread."""
        if self.is_downloading:
            messagebox.showinfo("Info", "A download is already in progress.")
            return
        
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please provide a URL.")
            return
        
        output_file = filedialog.asksaveasfilename(
            title="Save File",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf"), ("Image files", "*.jpg"), ("All files", "*.*")]
        )
        if not output_file:
            messagebox.showerror("Error", "Please choose a valid location to save the file.")
            return

        self.is_downloading = True
        self.download_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        
        threading.Thread(target=self.download_in_thread, args=(url, output_file)).start()
    
    def download_in_thread(self, url, output_file):
        """Download in a separate thread to keep GUI responsive."""
        self.progress_bar['value'] = 0
        self.is_paused = False
        
        def progress_callback(progress, speed, time_remaining):
            self.progress_bar['value'] = progress
            self.speed_label.config(text=f"Download Speed: {speed / 1024:.2f} KB/s")
            self.time_remaining_label.config(text=f"Time Remaining: {time_remaining:.2f}s")
        
        success = download_content(url, output_file, self.pause_event, self.update_log, progress_callback)
        
        self.is_downloading = False
        self.download_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        
        if success:
            self.progress_bar['value'] = 100
            messagebox.showinfo("Success", f"Download completed and saved to {output_file}")
            self.save_download_history(url, output_file)
        else:
            messagebox.showerror("Error", "Download failed.")
    
    def save_download_history(self, url, file_path):
        """Save the download history after each download."""
        history_file = "download_history.json"
        try:
            with open(history_file, "r") as file:
                history = json.load(file)
        except FileNotFoundError:
            history = []

        history.append({"url": url, "file_path": file_path})

        with open(history_file, "w") as file:
            json.dump(history, file, indent=4)

    def toggle_pause(self):
        """Toggle the pause/resume state."""
        if self.is_paused:
            self.pause_event.set()  # Resume download
            self.pause_button.config(text="Pause")
            self.is_paused = False
        else:
            self.pause_event.clear()  # Pause download
            self.pause_button.config(text="Resume")
            self.is_paused = True
    
    def show_history(self):
        """Show the download history in a new window."""
        try:
            with open("download_history.json", "r") as file:
                history = json.load(file)
        except FileNotFoundError:
            messagebox.showinfo("No History", "No download history available.")
            return

        history_window = tk.Toplevel(self.root)
        history_window.title("Download History")

        for record in history:
            tk.Label(history_window, text=f"URL: {record['url']} - File: {record['file_path']}").pack()

if __name__ == "__main__":
    root = tk.Tk()
    gui = DownloaderGUI(root)
    root.mainloop()

#!/usr/bin/env python3
"""
Vulnerable Desktop Application
A simple desktop app with intentional vulnerabilities for testing.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import os
import sys
import ctypes
from ctypes import wintypes
import threading

class VulnerableDesktopApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vulnerable Desktop App")
        self.root.geometry("600x400")
        
        # Vulnerable global variables
        self.buffer = "A" * 64  # Buffer overflow target
        self.admin_password = "admin123"
        self.user_level = "user"
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface with vulnerable components."""
        
        # Title
        title = tk.Label(self.root, text="Vulnerable Desktop Application", font=("Arial", 16))
        title.pack(pady=10)
        
        # Buffer overflow test
        tk.Label(self.root, text="Buffer Overflow Test:").pack()
        self.buffer_entry = tk.Entry(self.root, width=50)
        self.buffer_entry.pack()
        tk.Button(self.root, text="Test Buffer", command=self.test_buffer_overflow).pack()
        
        # File inclusion vulnerability
        tk.Label(self.root, text="File Reader:").pack()
        self.file_entry = tk.Entry(self.root, width=50)
        self.file_entry.pack()
        tk.Button(self.root, text="Read File", command=self.read_file).pack()
        
        # Command injection
        tk.Label(self.root, text="System Command:").pack()
        self.cmd_entry = tk.Entry(self.root, width=50)
        self.cmd_entry.pack()
        tk.Button(self.root, text="Execute", command=self.execute_command).pack()
        
        # Privilege escalation
        tk.Label(self.root, text="Admin Panel:").pack()
        self.admin_entry = tk.Entry(self.root, width=50, show="*")
        self.admin_entry.pack()
        tk.Button(self.root, text="Login as Admin", command=self.admin_login).pack()
        
        # Status
        self.status_label = tk.Label(self.root, text="Status: User Level", fg="blue")
        self.status_label.pack(pady=10)
    
    def test_buffer_overflow(self):
        """Vulnerable buffer overflow function."""
        try:
            # Vulnerable: No bounds checking
            user_input = self.buffer_entry.get()
            self.buffer = user_input  # Direct assignment without length check
            
            # Simulate buffer overflow effect
            if len(user_input) > 64:
                messagebox.showinfo("Buffer Overflow", f"Buffer overflow detected! Input length: {len(user_input)}")
                # In a real scenario, this would crash or allow code execution
            else:
                messagebox.showinfo("Buffer", f"Buffer updated: {self.buffer}")
        except Exception as e:
            messagebox.showerror("Error", f"Buffer error: {e}")
    
    def read_file(self):
        """Vulnerable file inclusion."""
        try:
            file_path = self.file_entry.get()
            # Vulnerable: No path validation
            with open(file_path, 'r') as f:
                content = f.read()
            messagebox.showinfo("File Content", f"File content:\n{content[:500]}...")
        except Exception as e:
            messagebox.showerror("Error", f"File read error: {e}")
    
    def execute_command(self):
        """Vulnerable command injection."""
        try:
            command = self.cmd_entry.get()
            # Vulnerable: Direct command execution
            result = subprocess.check_output(command, shell=True, text=True)
            messagebox.showinfo("Command Result", f"Output:\n{result}")
        except Exception as e:
            messagebox.showerror("Error", f"Command error: {e}")
    
    def admin_login(self):
        """Vulnerable authentication."""
        try:
            password = self.admin_entry.get()
            # Vulnerable: Simple string comparison
            if password == self.admin_password:
                self.user_level = "admin"
                self.status_label.config(text="Status: Admin Level", fg="red")
                messagebox.showinfo("Success", "Logged in as admin!")
            else:
                messagebox.showerror("Error", "Invalid password")
        except Exception as e:
            messagebox.showerror("Error", f"Login error: {e}")
    
    def run(self):
        """Start the application."""
        self.root.mainloop()

if __name__ == "__main__":
    app = VulnerableDesktopApp()
    app.run() 
import customtkinter as ctk
from tkinter import messagebox
from php_installer.py import install_php
from server_manager import ServerManager

class PocketMinePanel:
    def __init__(self, root):
        self.root = root
        self.root.title("PocketMine-MP Panel")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)

        self.label = ctk.CTkLabel(self.frame, text="PocketMine-MP Control Panel", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=12, padx=10)

        self.start_button = ctk.CTkButton(self.frame, text="Start Server", command=self.start_server)
        self.start_button.pack(pady=10)

        self.stop_button = ctk.CTkButton(self.frame, text="Stop Server", command=self.stop_server)
        self.stop_button.pack(pady=10)

        self.update_button = ctk.CTkButton(self.frame, text="Update Server", command=self.update_server)
        self.update_button.pack(pady=10)

        self.console = ctk.CTkTextbox(self.frame, width=400, height=200)
        self.console.pack(pady=10)

        self.server_manager = ServerManager()
        self.install_php()

    def install_php(self):
        try:
            install_php()
            messagebox.showinfo("Installation", "PHP installed successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def start_server(self):
        self.server_manager.start_server()
        self.read_output()

    def read_output(self):
        output = self.server_manager.read_output()
        if output:
            self.console.insert("end", output)
            self.console.see("end")
        self.root.after(100, self.read_output)

    def stop_server(self):
        self.server_manager.stop_server()

    def update_server(self):
        try:
            install_php()
            self.server_manager.update_server()
            messagebox.showinfo("Update", "Server and PHP updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = ctk.CTk()
    app = PocketMinePanel(root)
    root.mainloop()

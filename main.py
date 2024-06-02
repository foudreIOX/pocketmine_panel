import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
import tkinter as tk
import shutil
import os
import yaml  # Ensure PyYAML is installed
from php_installer import install_php
from server_manager import ServerManager

class FileExplorer:
    def __init__(self, parent, directory, file_type="PHAR Files", extensions=[("PHAR Files", "*.phar")]):
        self.parent = parent
        self.directory = directory
        self.file_type = file_type
        self.extensions = extensions

        self.tree = ttk.Treeview(parent, selectmode='browse', style="Custom.Treeview")
        self.tree.heading("#0", text=file_type, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.populate_tree()

        self.button_frame = ctk.CTkFrame(parent)
        self.button_frame.pack(pady=10, fill="x")

        self.add_button = ctk.CTkButton(self.button_frame, text=f"Add {file_type}", command=self.add_file, font=ctk.CTkFont(size=16, weight="bold"))
        self.add_button.pack(side="left", padx=5, pady=5)

        self.remove_button = ctk.CTkButton(self.button_frame, text=f"Remove {file_type}", command=self.remove_file, font=ctk.CTkFont(size=16, weight="bold"))
        self.remove_button.pack(side="left", padx=5, pady=5)

    def populate_tree(self):
        if os.path.exists(self.directory):
            for item in os.listdir(self.directory):
                self.tree.insert("", "end", text=item, values=(item,))
        else:
            messagebox.showwarning("Directory Not Found", f"The directory '{self.directory}' does not exist. It will be created when the server starts.")

    def add_file(self):
        file_path = filedialog.askopenfilename(title=f"Select {self.file_type}", filetypes=self.extensions)
        if file_path:
            shutil.copy(file_path, self.directory)
            self.tree.insert("", "end", text=os.path.basename(file_path), values=(os.path.basename(file_path),))
            messagebox.showinfo(f"{self.file_type} Added", f"{self.file_type} {os.path.basename(file_path)} added successfully!")

    def remove_file(self):
        selected_item = self.tree.selection()
        if selected_item:
            file_name = self.tree.item(selected_item, "text")
            file_path = os.path.join(self.directory, file_name)
            if messagebox.askyesno(f"Remove {self.file_type}", f"Are you sure you want to remove {file_name}?"):
                os.remove(file_path)
                self.tree.delete(selected_item)
                messagebox.showinfo(f"{self.file_type} Removed", f"{self.file_type} {file_name} removed successfully!")
        else:
            messagebox.showwarning("No Selection", f"Please select a {self.file_type} to remove.")

class PluginDataExplorer:
    def __init__(self, parent, directory):
        self.parent = parent
        self.directory = directory

        self.tree = ttk.Treeview(parent, selectmode='browse', style="Custom.Treeview")
        self.tree.heading("#0", text="Plugin Data", anchor="w")
        self.tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.populate_tree()

        self.editor_frame = ctk.CTkFrame(parent)
        self.editor_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.editor_label = ctk.CTkLabel(self.editor_frame, text="Config Editor", font=ctk.CTkFont(size=18, weight="bold"))
        self.editor_label.pack(pady=10)

        self.text_editor = ctk.CTkTextbox(self.editor_frame, font=ctk.CTkFont(size=14))
        self.text_editor.pack(fill="both", expand=True, padx=10, pady=10)

        self.save_button = ctk.CTkButton(self.editor_frame, text="Save Config", command=self.save_config, font=ctk.CTkFont(size=16, weight="bold"))
        self.save_button.pack(pady=10)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def populate_tree(self):
        if os.path.exists(self.directory):
            for root, dirs, files in os.walk(self.directory):
                for file in files:
                    if file.endswith('.yml'):
                        file_path = os.path.join(root, file)
                        self.tree.insert("", "end", text=file_path, values=(file_path,))
        else:
            messagebox.showwarning("Directory Not Found", f"The directory '{self.directory}' does not exist. It will be created when the server starts.")

    def on_tree_select(self, event):
        selected_item = self.tree.selection()[0]
        file_path = self.tree.item(selected_item, "text")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                config_content = file.read()
                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", config_content)
        else:
            messagebox.showwarning("File Not Found", f"The file '{file_path}' does not exist.")

    def save_config(self):
        selected_item = self.tree.selection()[0]
        file_path = self.tree.item(selected_item, "text")
        with open(file_path, 'w') as file:
            config_content = self.text_editor.get("1.0", "end")
            file.write(config_content)
        messagebox.showinfo("Config Saved", f"Config file {file_path} saved successfully!")

class PocketMinePanel:
    def __init__(self, root):
        self.root = root
        self.root.title("PocketMine-MP Panel")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Maximize the window
        self.root.state('zoomed')

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)

        self.label = ctk.CTkLabel(self.frame, text="PocketMine-MP Control Panel", font=ctk.CTkFont(size=24, weight="bold"))
        self.label.pack(pady=12, padx=10)

        # Configure style for the notebook tabs and Treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background='#333333', borderwidth=0)
        style.configure("TNotebook.Tab", font=("Helvetica", 20, 'bold'), padding=[30, 15], background='#333333', foreground='white')
        style.map("TNotebook.Tab", background=[("selected", "#444444")], foreground=[("selected", "white")])

        style.configure("Custom.Treeview", font=("Helvetica", 20), rowheight=40, background='#333333', fieldbackground='#333333', foreground='white')
        style.configure("Custom.Treeview.Heading", font=("Helvetica", 22, 'bold'), background='#333333', foreground='white')

        self.notebook = ttk.Notebook(self.frame, style="TNotebook")
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        self.main_tab = ctk.CTkFrame(self.notebook)
        self.plugins_tab = ctk.CTkFrame(self.notebook)
        self.plugin_data_tab = ctk.CTkFrame(self.notebook)
        self.server_config_tab = ctk.CTkFrame(self.notebook)
        self.texture_pack_tab = ctk.CTkFrame(self.notebook)

        self.notebook.add(self.main_tab, text="Main")
        self.notebook.add(self.plugins_tab, text="Plugins")
        self.notebook.add(self.plugin_data_tab, text="Plugin Data")
        self.notebook.add(self.server_config_tab, text="Server Config")
        self.notebook.add(self.texture_pack_tab, text="Texture Packs")

        self.start_button = ctk.CTkButton(self.main_tab, text="Start/Restart Server", command=self.start_server, font=ctk.CTkFont(size=16, weight="bold"))
        self.start_button.pack(pady=10)

        self.update_button = ctk.CTkButton(self.main_tab, text="Update Server", command=self.update_server, font=ctk.CTkFont(size=16, weight="bold"))
        self.update_button.pack(pady=10)

        self.console = ctk.CTkTextbox(self.main_tab, font=ctk.CTkFont(size=14))
        self.console.pack(pady=10, fill="both", expand=True)

        self.command_entry = ctk.CTkEntry(self.main_tab, placeholder_text="Enter command here", font=ctk.CTkFont(size=14))
        self.command_entry.pack(pady=10, fill="x")
        self.command_entry.bind("<Return>", self.send_command)  # Bind the Enter key to send_command

        self.file_explorer = FileExplorer(self.plugins_tab, "./plugins")

        self.plugin_data_explorer = PluginDataExplorer(self.plugin_data_tab, "./plugin_data")

        self.server_manager = ServerManager()
        self.install_php()

        self.create_server_config_tab()
        self.create_texture_pack_tab()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def install_php(self):
        try:
            install_php()
            messagebox.showinfo("Installation", "PHP installed successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def start_server(self):
        self.server_manager.restart_server()
        self.read_output()

    def read_output(self):
        output = self.server_manager.read_output()
        if output:
            self.console.insert("end", output)
            self.console.see("end")
        self.root.after(100, self.read_output)

    def send_command(self, event=None):
        command = self.command_entry.get()
        self.server_manager.write_command(command)
        self.command_entry.delete(0, 'end')

    def update_server(self):
        try:
            self.server_manager.update_server()
            messagebox.showinfo("Update", "Server updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_closing(self):
        self.server_manager.stop_server()
        self.root.destroy()

    def create_server_config_tab(self):
        self.server_config_editor_frame = ctk.CTkFrame(self.server_config_tab)
        self.server_config_editor_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.server_config_editor_label = ctk.CTkLabel(self.server_config_editor_frame, text="Server Config Editor", font=ctk.CTkFont(size=18, weight="bold"))
        self.server_config_editor_label.pack(pady=10)

        self.server_config_text_editor = ctk.CTkTextbox(self.server_config_editor_frame, font=ctk.CTkFont(size=14))
        self.server_config_text_editor.pack(fill="both", expand=True, padx=10, pady=10)

        self.server_config_save_button = ctk.CTkButton(self.server_config_editor_frame, text="Save Config", command=self.save_server_config, font=ctk.CTkFont(size=16, weight="bold"))
        self.server_config_save_button.pack(pady=10)

        self.load_server_config()

    def load_server_config(self):
        if os.path.exists("./server.properties"):
            with open("./server.properties", "r") as file:
                config_content = file.read()
                self.server_config_text_editor.delete("1.0", "end")
                self.server_config_text_editor.insert("1.0", config_content)
        else:
            messagebox.showwarning("File Not Found", "Server config file 'server.properties' does not exist. It will be created when the server starts.")

    def save_server_config(self):
        try:
            with open("./server.properties", "w") as file:
                config_content = self.server_config_text_editor.get("1.0", "end")
                file.write(config_content)
            messagebox.showinfo("Config Saved", "Server config file saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_texture_pack_tab(self):
        self.texture_pack_editor_frame = ctk.CTkFrame(self.texture_pack_tab)
        self.texture_pack_editor_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.texture_pack_editor_label = ctk.CTkLabel(self.texture_pack_editor_frame, text="Texture Pack Config Editor", font=ctk.CTkFont(size=18, weight="bold"))
        self.texture_pack_editor_label.grid(row=0, column=0, padx=10, pady=10)

        self.texture_pack_text_editor = ctk.CTkTextbox(self.texture_pack_editor_frame, font=ctk.CTkFont(size=14))
        self.texture_pack_text_editor.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.texture_pack_save_button = ctk.CTkButton(self.texture_pack_editor_frame, text="Save Config", command=self.save_texture_pack_config, font=ctk.CTkFont(size=16, weight="bold"))
        self.texture_pack_save_button.grid(row=2, column=0, padx=10, pady=10)

        self.texture_pack_editor_frame.grid_rowconfigure(1, weight=1)
        self.texture_pack_editor_frame.grid_columnconfigure(0, weight=1)

        self.load_texture_pack_config()

        self.texture_pack_file_explorer = FileExplorer(self.texture_pack_tab, "./resource_packs", "Texture Pack", [("ZIP Files", "*.zip")])
        self.texture_pack_file_explorer.tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    def load_texture_pack_config(self):
        if os.path.exists("./resource_packs/resource_packs.yml"):
            with open("./resource_packs/resource_packs.yml", "r") as file:
                config_content = file.read()
                self.texture_pack_text_editor.delete("1.0", "end")
                self.texture_pack_text_editor.insert("1.0", config_content)
        else:
            messagebox.showwarning("File Not Found", "Texture pack config file 'resource_packs.yml' does not exist. It will be created when the server starts.")

    def save_texture_pack_config(self):
        try:
            with open("./resource_packs/resource_packs.yml", "w") as file:
                config_content = self.texture_pack_text_editor.get("1.0", "end")
                file.write(config_content)
            messagebox.showinfo("Config Saved", "Texture pack config file saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = ctk.CTk()
    app = PocketMinePanel(root)
    root.mainloop()

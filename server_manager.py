import subprocess
import os
import requests
import threading
import queue
import psutil
import shutil
import zipfile
import hashlib
import ctypes
import sys

class ServerManager:
    def __init__(self):
        self.process = None
        self.queue = queue.Queue()
        self.running = False
        self.server_dir = "./"

    def start_server(self):
        if self.process is None:
            self.process = subprocess.Popen(
                ["start.cmd"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                shell=True,
                encoding='utf-8',
                errors='replace'
            )
            self.running = True
            threading.Thread(target=self._enqueue_output, args=(self.process.stdout,)).start()
            threading.Thread(target=self._enqueue_output, args=(self.process.stderr,)).start()
            print("Server started.")

    def restart_server(self):
        self.stop_server()
        self.start_server()

    def stop_server(self):
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = proc.info['cmdline']
            if cmdline and 'PocketMine-MP.phar' in cmdline:
                print(f"Stopping existing server with PID {proc.info['pid']}")
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                    print(f"Server with PID {proc.info['pid']} stopped.")
                except subprocess.TimeoutExpired:
                    proc.kill()
                    print(f"Server with PID {proc.info['pid']} forcefully stopped.")
        self.process = None
        self.running = False

    def _enqueue_output(self, stream):
        try:
            for line in iter(stream.readline, ''):
                self.queue.put(line)
        except Exception as e:
            print(f"Error reading output: {e}")
        finally:
            stream.close()

    def read_output(self):
        output = []
        while not self.queue.empty():
            try:
                output.append(self.queue.get_nowait())
            except queue.Empty:
                break
        return ''.join(output)

    def write_command(self, command):
        if self.process and self.process.stdin:
            try:
                print(f"Writing command to server: {command}")
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
                print(f"Command sent: {command}")
            except OSError as e:
                print(f"Error writing command to server: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
        else:
            print("Server process is not running or stdin is not available.")

    def get_file_hash(self, filepath):
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def update_server(self):
        try:
            self.install_php_if_needed()

            url_phar = "https://github.com/pmmp/PocketMine-MP/releases/latest/download/PocketMine-MP.phar"
            response = requests.get(url_phar)
            with open("PocketMine-MP.phar", "wb") as file:
                file.write(response.content)

            url_cmd = "https://github.com/pmmp/PocketMine-MP/releases/latest/download/start.cmd"
            response = requests.get(url_cmd)
            with open("start.cmd", "wb") as file:
                file.write(response.content)

            print("Server updated successfully!")
        except Exception as e:
            print(f"Error updating server: {e}")
            raise

    def install_php_if_needed(self):
        try:
            project_dir = "./"
            bin_dir = os.path.join(project_dir, 'bin')
            php_exe_path = os.path.join(bin_dir, 'php', 'php.exe')

            if os.path.exists(php_exe_path):
                print("PHP is already installed, skipping installation.")
                return

            url = "https://github.com/pmmp/PHP-Binaries/releases/download/php-8.2-latest/PHP-Windows-x64-PM5.zip"
            php_zip_path = "php.zip"
            php_dir = "php"

            print("Downloading PHP...")
            response = requests.get(url)
            with open(php_zip_path, "wb") as file:
                file.write(response.content)

            print("Extracting PHP...")
            with zipfile.ZipFile(php_zip_path, 'r') as zip_ref:
                zip_ref.extractall(php_dir)

            os.remove(php_zip_path)

            if not os.path.exists(bin_dir):
                os.makedirs(bin_dir)

            source_php_dir = os.path.join(php_dir, 'bin', 'php')
            destination_php_dir = os.path.join(bin_dir, 'php')

            if os.path.exists(source_php_dir):
                print(f"Moving {source_php_dir} to {destination_php_dir}...")
                shutil.move(source_php_dir, destination_php_dir)
                shutil.rmtree(php_dir)
            else:
                print("The 'php' directory was not found in the extracted files.")

            if self.check_php_installation(bin_dir):
                print("PHP installed successfully!")
            else:
                print("PHP installation failed.")
        except Exception as e:
            print(f"Error installing PHP: {e}")
            raise

    def check_php_installation(self, bin_dir):
        php_exe_path = os.path.join(bin_dir, 'php', 'php.exe')
        if not os.path.exists(php_exe_path):
            print(f"Couldn't find PHP binary at {php_exe_path}.")
            return False
        try:
            result = subprocess.run([php_exe_path, "-v"], capture_output=True, text=True)
            if result.returncode == 0:
                print("PHP is installed and working correctly.")
                return True
            else:
                print("PHP binary is not working correctly.")
                return False
        except Exception as e:
            print(f"Error checking PHP installation: {e}")
            return False

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    try:
        if sys.version_info[0] == 3 and sys.version_info[1] >= 5:
            subprocess.run(['python', __file__], check=True, shell=True)
        else:
            raise RuntimeError("Python 3.5 or higher is required to run this script as administrator.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Failed to run script as administrator.")

if __name__ == "__main__":
    if is_admin():
        manager = ServerManager()
        manager.update_server()

        def read_loop():
            while True:
                try:
                    if manager.running:
                        output = manager.read_output()
                        if output:
                            print(output, end='')
                except KeyboardInterrupt:
                    if manager.running:
                        print("Stopping server...")
                        manager.stop_server()
                    print("Exiting program...")
                    break

        manager.start_server()
        read_loop()
    else:
        print("This script requires administrator privileges. Attempting to restart as administrator...")
        try:
            run_as_admin()
        except RuntimeError as e:
            print(e)

import subprocess
import os

class ServerManager:
    def __init__(self):
        self.process = None

    def start_server(self):
        if self.process is None:
            self.process = subprocess.Popen(["php", "PocketMine-MP.phar"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("Server started.")
    
    def stop_server(self):
        if self.process:
            self.process.terminate()
            self.process = None
            print("Server stopped.")

    def read_output(self):
        if self.process:
            output = self.process.stdout.read(1)
            return output
        return None

    def update_server(self):
        try:
            url = "https://jenkins.pmmp.io/job/PocketMine-MP/lastSuccessfulBuild/artifact/PocketMine-MP.phar"
            response = requests.get(url)
            with open("PocketMine-MP.phar", "wb") as file:
                file.write(response.content)
            print("Server updated successfully!")
        except Exception as e:
            print(f"Error updating server: {e}")
            raise

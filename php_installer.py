import os
import requests
import zipfile
import shutil
import stat
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if sys.version_info[0] == 3 and sys.version_info[1] >= 5:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        raise RuntimeError("This script requires Python 3.5 or higher.")

def set_permissions(file_path):
    try:
        os.chmod(file_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        print(f"Permissions set for {file_path}")
    except PermissionError as pe:
        print(f"Permission error while setting permissions for {file_path}: {pe}")
    except Exception as e:
        print(f"Unexpected error while setting permissions for {file_path}: {e}")

def update_path_env(project_dir):
    php_bin_path = os.path.join(project_dir, 'bin', 'php', 'php.exe')
    if php_bin_path not in os.environ['PATH']:
        os.environ['PATH'] += os.pathsep + php_bin_path
        print(f"Updated PATH environment variable with {php_bin_path}")

def check_php_installation(project_dir):
    php_exe_path = os.path.join(project_dir, 'bin', 'php', 'php.exe')
    if not os.path.exists(php_exe_path):
        print(f"Couldn't find PHP binary at {php_exe_path}.")
        return False
    try:
        result = os.system(f'"{php_exe_path}" -v')
        if result == 0:
            print("PHP is installed and working correctly.")
            return True
        else:
            print("PHP binary is not working correctly.")
            return False
    except Exception as e:
        print(f"Error checking PHP installation: {e}")
        return False

def install_php():
    try:
        url = "https://github.com/pmmp/PHP-Binaries/releases/download/php-8.2-latest/PHP-Windows-x64-PM5.zip"
        php_zip_path = "php.zip"
        php_dir = "php"
        project_dir = r"./"  # Répertoire racine de votre projet
        bin_dir = os.path.join(project_dir, 'bin')

        # Si le dossier bin existe déjà, sauter l'installation
        if os.path.exists(bin_dir):
            print("PHP is already installed, skipping installation.")
            return

        # Télécharger PHP
        print("Downloading PHP...")
        response = requests.get(url)
        with open(php_zip_path, "wb") as file:
            file.write(response.content)

        # Décompresser PHP
        print("Extracting PHP...")
        with zipfile.ZipFile(php_zip_path, 'r') as zip_ref:
            zip_ref.extractall(php_dir)

        os.remove(php_zip_path)

        # Créer le dossier 'bin' dans le répertoire racine du projet
        if not os.path.exists(bin_dir):
            os.makedirs(bin_dir)

        # Déplacer le dossier 'php' du dossier 'php/bin' vers le répertoire 'bin'
        source_php_dir = os.path.join(php_dir, 'bin', 'php')
        destination_php_dir = os.path.join(bin_dir, 'php')

        if os.path.exists(source_php_dir):
            print(f"Moving {source_php_dir} to {destination_php_dir}...")
            shutil.move(source_php_dir, destination_php_dir)
            shutil.rmtree(php_dir)
        else:
            print("The 'php' directory was not found in the extracted files.")

        update_path_env(project_dir)
        if check_php_installation(project_dir):
            print("PHP installed successfully!")
        else:
            print("PHP installation failed.")
    except Exception as e:
        print(f"Error installing PHP: {e}")
        raise

if __name__ == "__main__":
    if is_admin():
        install_php()
    else:
        print("This script requires administrator privileges. Attempting to restart as administrator...")
        try:
            run_as_admin()
        except RuntimeError as e:
            print(e)

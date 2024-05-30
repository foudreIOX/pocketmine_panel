import os
import requests
import zipfile

def install_php():
    try:
        url = "https://windows.php.net/downloads/releases/php-8.1.0-Win32-vs16-x64.zip"  # Modify URL for latest PHP version
        php_zip_path = "php.zip"
        php_dir = "php"

        # Download PHP
        response = requests.get(url)
        with open(php_zip_path, "wb") as file:
            file.write(response.content)

        # Unzip PHP
        with zipfile.ZipFile(php_zip_path, 'r') as zip_ref:
            zip_ref.extractall(php_dir)

        os.remove(php_zip_path)

        # Set PHP path
        os.environ["PATH"] += os.pathsep + os.path.abspath(php_dir)
        print("PHP installed successfully!")
    except Exception as e:
        print(f"Error installing PHP: {e}")
        raise

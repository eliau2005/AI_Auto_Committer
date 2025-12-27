import os
import subprocess
import sys
import shutil

# שם הקובץ הראשי שלך
MAIN_SCRIPT = "main.py"
# שם האפליקציה שתופיע
APP_NAME = "AI_Auto_Committer"

def install_package(package, import_name=None):
    """מתקין חבילה אם היא חסרה"""
    if import_name is None:
        import_name = package
    
    print(f"Checking for {import_name}...")
    try:
        __import__(import_name)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def get_customtkinter_path():
    """מוצא את הנתיב של ספריית CustomTkinter להוספה ל-EXE"""
    import customtkinter
    return os.path.dirname(customtkinter.__file__)

def build():
    # 1. התקנת דרישות
    # PyInstaller לפעמים דורש אות גדולה בייבוא
    install_package("pyinstaller", "PyInstaller") 
    install_package("customtkinter")
    
    # 2. קבלת נתיב הנתונים של customtkinter
    try:
        ctk_path = get_customtkinter_path()
        print(f"CustomTkinter path found: {ctk_path}")
    except ImportError:
        print("Error: Could not import customtkinter even after install attempt.")
        return

    # 3. בניית הפקודה ל-PyInstaller
    # התיקון: שימוש ב-sys.executable כדי להריץ את המודול ישירות
    separator = ";" if os.name == 'nt' else ":"
    add_data_arg = f"{ctk_path}{separator}customtkinter/"
    
    cmd = [
        sys.executable, "-m", "PyInstaller", # <--- התיקון כאן
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", APP_NAME,
        "--icon", "icon.ico",
        "--add-data", add_data_arg,
        MAIN_SCRIPT
    ]
    
    print("Running PyInstaller module... This may take a minute.")
    # הדפסת הפקודה לדיבוג
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "="*50)
        print("BUILD SUCCESSFUL!")
        print(f"Your exe file is located in the 'dist' folder: dist/{APP_NAME}.exe")
        print("="*50)
    except subprocess.CalledProcessError as e:
        print(f"\nError during build: {e}")
    except FileNotFoundError:
        print("\nError: Still cannot find the python executable path.")

if __name__ == "__main__":
    build()
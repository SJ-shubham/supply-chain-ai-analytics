import os
import sys
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def main():
    print("============================================================")
    print("  SUPPLY CHAIN AI ANALYTICS PLATFORM — BOOTSTRAP RUNNER")
    print("============================================================")
    
    app_path = os.path.join(PROJECT_ROOT, "web_app", "app.py")
    if not os.path.exists(app_path):
        print(f"Error: Application server file not found at {app_path}")
        sys.exit(1)
        
    venv_python = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
    python_bin = venv_python if os.path.exists(venv_python) else sys.executable

    print(f"[OK] Found Application Server: {app_path}")
    print(f"[OK] Using Python Executable: {python_bin}")
    print("[OK] Starting Flask Server at http://127.0.0.1:5000/ ...\n")
    
    # Run Flask App
    subprocess.run([python_bin, app_path])

if __name__ == "__main__":
    main()

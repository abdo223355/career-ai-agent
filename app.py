"""
Entry point for the Career AI Agent application.
Launches the production Streamlit user interface.
"""
import os
import sys
import subprocess

def main():
    ui_path = os.path.join(os.path.dirname(__file__), "src", "ui", "chat.py")
    cmd = [sys.executable, "-m", "streamlit", "run", ui_path, "--server.port", "8501", "--server.address", "0.0.0.0"]
    print(f"🚀 Launching Career AI Agent via: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()

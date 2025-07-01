#!/usr/bin/env python3

import sys
import os
import subprocess
import re
from pathlib import Path
from datetime import datetime

def main():
    # Check if URL argument is provided
    if len(sys.argv) < 2:
        print("[!] Error: Please provide a URL to scan")
        print("Usage: python3 nuclei_scanner.py https://example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Validate URL format (basic check)
    url_pattern = re.compile(r'^https?://')
    if not url_pattern.match(url):
        print("[!] Error: Please provide a valid URL starting with http:// or https://")
        print("Usage: python3 nuclei_scanner.py https://example.com")
        sys.exit(1)
    
    # Check if nuclei is installed
    if not check_nuclei_installed():
        print("[!] Error: nuclei is not installed or not in PATH")
        print("Please install nuclei first: https://nuclei.projectdiscovery.io/nuclei/get-started/")
        sys.exit(1)
    
    # Activate virtual environment if it exists
    activate_venv()
    
    # Run the nuclei scan
    print(f"[*] Starting Nuclei scan for: {url}")
    exit_code = run_nuclei_scan_and_save(url)
    
    # Check the exit code
    if exit_code == 0:
        print("[+] Scan completed successfully")
    else:
        print("[!] Scan completed with errors or warnings")
    
    sys.exit(exit_code)

def check_nuclei_installed():
    """Check if nuclei is installed and available in PATH"""
    try:
        result = subprocess.run(
            ["nuclei", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def activate_venv():
    """Activate virtual environment if it exists"""
    venv_path = Path("venv")
    if venv_path.exists() and venv_path.is_dir():
        print("[*] Virtual environment found")
        # Note: In Python, we can't directly activate a venv like in bash
        # The venv should be activated before running this script
        # or we can modify the Python path to include the venv
        venv_python = venv_path / "bin" / "python3"
        if venv_python.exists():
            print("[*] Using virtual environment Python")
            # We could potentially restart with the venv Python, but for now
            # we'll just note that it exists
        else:
            print("[*] Virtual environment found but Python not detected")

def run_nuclei_scan_and_save(url):
    """Run nuclei scan and save results to file"""
    try:
        # Call run_nuclei_scan with the URL
        scan_output = run_nuclei_scan(url)
        
        if scan_output is None:
            print("[!] Nuclei scan failed or returned no output")
            return 1
            
        # Create outputs directory if it doesn't exist
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp-based filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]  # Remove last 3 digits to get milliseconds
        filename = f"{timestamp}-scan.txt"
        filepath = os.path.join(output_dir, filename)

        # Save the scan output to file
        with open(filepath, "w") as f:
            f.write(scan_output)
        print(f"[*] Scan results saved as {filepath}")
        return 0

    except Exception as e:
        print(f"[!] Error running scan: {e}", file=sys.stderr)
        return 1

def run_nuclei_scan(url):
    """Run nuclei scan on the given URL"""
    # Build the command with absolute minimal settings
    command = [
        "nuclei",
        "-u", url
    ]
    
    # Debug: Print the exact command being executed
    print(f"[DEBUG] Executing command: {' '.join(command)}")
    
    try:
        # Run the command with very short timeout
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # Return output as string, not bytes
            timeout=600,  # Very long timeout
            check=False  # Don't raise CalledProcessError on non-zero exit
        )
        
        print("Nuclei output:")
        print(result.stdout)
        
        # Check if process was killed by SIGKILL (exit code -9)
        if result.returncode == -9:
            print("[!] Warning: Nuclei process was killed by SIGKILL (likely due to memory/resource limits)")
            print("[!] This indicates the process was using too much memory or CPU")
            # Return partial output if available
            if result.stdout.strip():
                return result.stdout
            else:
                return None
      
        
        # Check for other non-zero exit codes
        if result.returncode != 0:
            print(f"[!] Nuclei exited with code {result.returncode}")
            if result.stderr:
                print("Nuclei error output:")
                print(result.stderr)
            # Return output even if exit code is non-zero, as some findings might be found
            return result.stdout if result.stdout.strip() else None
        
        return result.stdout
        
    except subprocess.TimeoutExpired:
        print("[!] Nuclei scan timed out after 25 seconds")
        return None
    except FileNotFoundError:
        print("[!] Error: nuclei command not found. Please ensure nuclei is installed and in PATH")
        return None
    except Exception as e:
        print(f"[!] Unexpected error running nuclei: {e}")
        return None

if __name__ == "__main__":
    main() 
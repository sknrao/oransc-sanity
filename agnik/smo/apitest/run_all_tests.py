#!/usr/bin/env python3
import sys
import subprocess

def run_script(script_name):
    print(f"\n============================================================")
    print(f"  Running: {script_name}")
    print(f"============================================================")
    try:
        # Run the script and stream output
        result = subprocess.run([sys.executable, script_name], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"\n❌ [{script_name}] failed. See output above.")
        return False
    except Exception as e:
        print(f"\n❌ Failed to run {script_name}: {e}")
        return False

if __name__ == "__main__":
    print("Starting O-RAN API Consolidated Tests...")
    
    scripts = [
        "test_influxdb.py",
        "test_kafka.py",
        "test_sdnr.py"
    ]
    
    # Optional test (needs port-forwarding)
    # scripts.append("test_minio.py")
    
    all_passed = True
    for script in scripts:
        if not run_script(script):
            all_passed = False
            
    print(f"\n============================================================")
    if all_passed:
        print("✅ ALL API TESTS PASSED!")
        sys.exit(0)
    else:
        print("❌ SOME API TESTS FAILED.")
        sys.exit(1)

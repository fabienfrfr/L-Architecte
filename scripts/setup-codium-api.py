#!/usr/bin/env python3
"""
VSCodium Configuration Utility for AgenticArchitect (TheArchitect).
This script enables Proposed APIs for specific extensions required for
remote development, testing (Pytest), and debugging within Kubernetes pods.
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

# Configuration: Extensions to authorize
REQUIRED_APIS = ["3timeslazy.vscodium-devpodcontainers", "jeanp413.open-remote-ssh"]


def clean_jsonc(content):
    """Remove C-style comments (// and /* */) from JSON string."""
    pattern = r"//.*|/\*[\s\S]*?\*/"
    return re.sub(pattern, "", content)


def setup_vscodium_configs():
    # 1. Locate argv.json for VSCodium
    # Path follows the standard Linux location for VSCodium OSS
    argv_path = Path.home() / ".vscode-oss" / "argv.json"

    print(f"[*] Target file: {argv_path}")

    if not argv_path.exists():
        print("[!] File not found. Creating a new configuration...")
        argv_path.parent.mkdir(parents=True, exist_ok=True)
        with open(argv_path, "w") as f:
            f.write("{\n}\n")

    # 2. Create a timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = argv_path.with_suffix(f".{timestamp}.bak")
    shutil.copy2(argv_path, backup_path)
    print(f"[*] Backup created: {backup_path}")

    # 3. Read and Parse JSONC
    try:
        with open(argv_path, "r") as f:
            raw_content = f.read()

        # Remove comments before parsing
        clean_content = clean_jsonc(raw_content)
        data = json.loads(clean_content) if clean_content.strip() else {}
    except Exception as e:
        print(f"[!] Error parsing existing configuration: {e}")
        print("[*] Initializing with empty configuration.")
        data = {}

    # 4. Inject Proposed APIs
    current_apis = data.get("enable-proposed-api", [])
    if not isinstance(current_apis, list):
        current_apis = []

    # Merge lists without duplicates
    updated_apis = list(set(current_apis + REQUIRED_APIS))
    data["enable-proposed-api"] = updated_apis

    # 5. Write back to disk
    with open(argv_path, "w") as f:
        json.dump(data, f, indent=4)

    print("[+] Successfully updated enable-proposed-api.")
    print("[+] Configuration complete. Please restart VSCodium.")


if __name__ == "__main__":
    try:
        setup_vscodium_configs()
    except Exception as fatal_error:
        print(f"[FATAL] Script failed: {fatal_error}")

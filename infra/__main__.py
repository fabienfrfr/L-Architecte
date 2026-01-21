import os
import textwrap
import subprocess
from pathlib import Path
import pulumi
import pulumi_ovh as ovh
from pulumi_command import remote

# --- Helpers ---
def get_script_content(filename: str) -> str:
    """Read the installation script from the scripts directory."""
    current_dir = Path(__file__).resolve().parent
    script_path = current_dir.parent / "scripts" / filename
    if not script_path.exists():
        raise FileNotFoundError(f"Could not find the script at {script_path}")
    return script_path.read_text(encoding="utf-8")

def ensure_config(config: pulumi.Config, key: str, default_value: str) -> str:
    """Check if a config key exists, otherwise write it to the YAML file."""
    value = config.get(key)
    if not value:
        pulumi.log.info(f"Config '{key}' not found. Initializing with: {default_value}")
        subprocess.run(["pulumi", "config", "set", key, default_value], check=True)
        return default_value
    return value

# --- Functions with Inputs ---

def manage_dns(domain: str, ip: str):
    """Update OVH DNS A Record for the given domain and IP."""
    return ovh.domain.ZoneRecord("thearchitect-a-record",
        zone=domain,
        subdomain="", # Root domain
        fieldtype="A",
        target=ip,
        ttl=3600
    )

# Hard reset (not used for now)
def rebuild_vps(vps_name: str, image_id: str):
    """Rebuild ovh provider vps"""
    return ovh.vps.Vps("vps-reinstall",
        name=vps_name,
        rebuild=True,
        image=image_id
    )

# Soft reset
def deploy(vps_host: str, vps_user: str):
    """Orchestrate deployment on the VPS."""
    script_content = get_script_content("install-tools.sh")

    connection = remote.ConnectionArgs(
        host=vps_host,
        user=vps_user,
        # Use local SSH agent for authentication
        agent_socket_path=os.environ.get("SSH_AUTH_SOCK"),    
        )

    raw_payload = f"""
    cat << 'EOF' > /tmp/install.sh
    {script_content}
    EOF
    chmod +x /tmp/install.sh
    bash /tmp/install.sh vps
    """
    cmd_payload = textwrap.dedent(raw_payload).strip()

    return remote.Command(
        "vps-setup-debug",
        connection=connection,
        create=cmd_payload,
        update=cmd_payload,
        triggers=[script_content],
        opts=pulumi.ResourceOptions(delete_before_replace=True)
    )

# --- Main Flow ---
config = pulumi.Config()

# 1. Inputs initialization (Lazy config)
vps_ip = ensure_config(config, "vps_ip", "51.254.138.196")
host   = ensure_config(config, "vps_host", "vps-5dc72e2c.vps.ovh.net")
user   = ensure_config(config, "vps_user", "ubuntu")
domain = ensure_config(config, "domain_name", "thearchitect.dev")


# 2. Execution
deploy_all = config.get_bool("all") or False

if deploy_all:
    pulumi.log.info("Full Deployment: Managing DNS + VPS Setup")
    dns_resource = manage_dns(domain, vps_ip)
else:
    pulumi.log.info("Standard Deployment: VPS Setup only (DNS skipped)")
    
setup_resource = deploy(host, user)

# 3. Exports
pulumi.export("vps_host", host)
pulumi.export("domain", domain)
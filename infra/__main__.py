import os
import textwrap
import subprocess
from pathlib import Path

import pulumi
import pulumi_ovh as ovh
import pulumi_kubernetes as k8s
from pulumi_command import remote

# --- Configuration Helpers ---

def get_script_content(filename: str) -> str:
    """
    Read the installation script from the local scripts directory.
    Ensures that the infrastructure state is tied to the script content.
    """
    current_dir = Path(__file__).resolve().parent
    script_path = current_dir.parent / "scripts" / filename
    if not script_path.exists():
        raise FileNotFoundError(f"Could not find the script at {script_path}")
    return script_path.read_text(encoding="utf-8")

def ensure_config(config: pulumi.Config, key: str, default_value: str) -> str:
    """
    Check if a config key exists, otherwise initialize it in the Pulumi YAML file.
    This facilitates 'Lazy' setup for new environments.
    """
    value = config.get(key)
    if not value:
        pulumi.log.info(f"Config '{key}' not found. Initializing with: {default_value}")
        subprocess.run(["pulumi", "config", "set", key, default_value], check=True)
        return default_value
    return value

# --- Infrastructure Management Functions ---

def rebuild_vps(vps_name: str, image_id: str) -> ovh.vps.Vps:
    """
    Hard Reset: Reinstalls the VPS using the OVH provider.
    WARNING: This wipes all data on the target VPS.
    """
    return ovh.vps.Vps("vps-reinstall",
        name=vps_name,
        rebuild=True,
        image=image_id
    )

def manage_dns_records(domain: str, ip: str) -> ovh.domain.ZoneRecord:
    """
    Ensures the DNS A record points to the current VPS IP address.
    """
    return ovh.domain.ZoneRecord("thearchitect-a-record",
        zone=domain,
        subdomain="", # Root domain
        fieldtype="A",
        target=ip,
        ttl=3600
    )

def bootstrap_vps_system(vps_host: str, vps_user: str, depend_on_resource=None) -> remote.Command:
    """
    Soft Reset / Provisioning: Executes the 'install-tools.sh' script via SSH.
    Prepares K3s, Docker, and system dependencies.
    """
    script_content = get_script_content("install-tools.sh")

    connection = remote.ConnectionArgs(
        host=vps_host,
        user=vps_user,
        agent_socket_path=os.environ.get("SSH_AUTH_SOCK"),    
    )

    install_payload = textwrap.dedent(f"""
        cat << 'EOF' > /tmp/install.sh
        {script_content}
        EOF
        chmod +x /tmp/install.sh
        bash /tmp/install.sh vps
    """).strip()

    return remote.Command(
        "vps-system-bootstrap",
        connection=connection,
        create=install_payload,
        update=install_payload,
        triggers=[script_content],
        opts=pulumi.ResourceOptions(
            delete_before_replace=True,
            depends_on=[depend_on_resource] if depend_on_resource else []
        )
    )

def deploy_kubernetes_resources(provider: k8s.Provider, image_tag: str):
    """
    Deploys the AgenticArchitect application stack to the K3s cluster.
    """
    app_labels = {"app": "architect"}
    
    return k8s.apps.v1.Deployment(
        "architect-deployment",
        spec={
            "selector": {"match_labels": app_labels},
            "replicas": 2, 
            "template": {
                "metadata": {"labels": app_labels},
                "spec": {
                    "containers": [{
                        "name": "architect",
                        "image": f"ghcr.io/fabienfrfr/architect:{image_tag}",
                        "ports": [{"container_port": 8080}]
                    }]
                }
            }
        },
        opts=pulumi.ResourceOptions(provider=provider)
    )

# --- Orchestration ---

def main():
    config = pulumi.Config()

    # 1. Config Initialization
    vps_ip   = ensure_config(config, "vps_ip", "51.254.138.196")
    vps_name = ensure_config(config, "vps_name", "vps-5dc72e2c.vps.ovh.net")
    user     = ensure_config(config, "vps_user", "ubuntu")
    domain   = ensure_config(config, "domain_name", "thearchitect.dev")
    image_id = config.get("image_id") or "ubuntu-24.04" # Default image

    # 2. Infrastructure Layer
    vps_resource = None
    if config.get_bool("hard_rebuild") or False:
        pulumi.log.warn("🚨 HARD REBUILD triggered. Reinstalling OS...")
        vps_resource = rebuild_vps(vps_name, image_id)

    if config.get_bool("dns") or False:
        manage_dns_records(domain, vps_ip)

    # 3. System Layer (SSH)
    # If we rebuild, the bootstrap must wait for the OS to be ready
    system_setup = bootstrap_vps_system(vps_name, user, depend_on_resource=vps_resource)

    # 4. Application Layer (K8s)
    kubeconfig = config.require_secret("kubeconfig")
    k8s_provider = k8s.Provider("vps-k8s-provider",
        kubeconfig=kubeconfig,
        opts=pulumi.ResourceOptions(depends_on=[system_setup])
    )

    deploy_kubernetes_resources(k8s_provider, "latest")

    # 5. Exports
    pulumi.export("vps_host", vps_name)
    pulumi.export("deployment_url", f"http://{domain}")

if __name__ == "__main__":
    main()
import os
import subprocess
import time
import base64
import logging
from typing import Any, Optional, List
from pathlib import Path

import pulumi
import ovh as ovh_sdk
from pulumi.dynamic import Resource, ResourceProvider, CreateResult
from pulumi_command import remote
import pulumi_kubernetes as k8s

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Architect")

# --- 1. Configuration Manager ---
class ArchitectConfig:
    def __init__(self):
        # Using the exact project config name from your original code
        self.p_cfg = pulumi.Config("AgenticArchitect-Infra")
        self.ovh_cfg = pulumi.Config("ovh")
        
        self.ovh_endpoint = self.ovh_cfg.get("endpoint") or "ovh-eu"
        
        # Deployment Flags (Restored and completed with your new request)
        self.should_infra = self.p_cfg.get_bool("setup_infra") or False
        self.should_system = self.p_cfg.get_bool("setup_system") or False
        self.should_deploy = self.p_cfg.get_bool("deploy_app") or False
        
        # Force reinstall trigger (using the timestamp strategy we discussed)
        force_val = self.p_cfg.get("force_reinstall")
        if force_val == "true":
            self.force_key = str(time.time())
        else:
            self.force_key = force_val or "stable"

        # VPS Info (Original values preserved)
        self.vps_name = self.p_cfg.get("vps_host") or "vps-5dc72e2c.vps.ovh.net"
        self.vps_ip = self.p_cfg.get("vps_ip") or "51.254.138.196"
        self.vps_user = self.p_cfg.get("vps_user") or "ubuntu"
        self.ubuntu_version = "24.04"

    @property
    def public_ssh_key(self) -> str:
        path = Path.home() / ".ssh" / "id_rsa.pub"
        return path.read_text().strip()

    @property
    def bootstrap_script(self) -> str:
        # Restored your exact path logic and file creation safety
        path = Path(__file__).resolve().parent.parent / "scripts" / "install-tools.sh"
        if not path.exists():
            path.parent.mkdir(exist_ok=True)
            path.write_text("#!/bin/bash\necho 'Hello from Architect!'")
        return path.read_text()

# --- 2. OVH Dynamic Provider ---
class VPSRebuildProvider(ResourceProvider):
    def create(self, props: Any) -> CreateResult:
        client = ovh_sdk.Client(
            endpoint=props['endpoint'],
            application_key=props['ak'],
            application_secret=props['as_key'],
            consumer_key=props['ck'],
        )
        vps, version = props['vps_name'], props['version']

        # Scan for Image ID (Restored your exact logic)
        image_ids = client.get(f"/vps/{vps}/images/available")
        target_id = next((i for i in image_ids if version in client.get(f"/vps/{vps}/images/available/{i}")['name'].lower()), None)
        
        if not target_id: raise Exception(f"Ubuntu {version} not found")

        # Start Rebuild (Restored all original OVH flags: installRTM and doNotSendPassword)
        logger.info(f"🚀 Rebuilding {vps}...")
        task = client.post(f"/vps/{vps}/rebuild", 
                           imageId=target_id, 
                           publicSshKey=props['ssh_key'], 
                           installRTM=False, 
                           doNotSendPassword=True)
        task_id = task.get('id')

        # Real-time Monitoring (Restored error handling and loop)
        while True:
            status = client.get(f"/vps/{vps}/tasks/{task_id}").get('state')
            if status == 'done': break
            if status == 'error': raise Exception("OVH Task Failed")
            time.sleep(10)

        # Clean local ssh
        try:
            domain = "thearchitect.dev"
            subprocess.run(["ssh-keygen", "-R", domain], capture_output=True)
        except Exception as e:
            logger.warning(f"⚠️ Could not clean known_hosts: {e}")

        return CreateResult(id_=f"rebuild-{task_id}", outs=props)

class VPSRebuild(Resource):
    def __init__(self, name: str, props: Any, opts=None):
        super().__init__(VPSRebuildProvider(), name, props, opts)

# --- 3. Provisioning Logic ---
def provision_system(vps_ip: str, cfg: ArchitectConfig, deps: List[pulumi.Resource]) -> Optional[remote.Command]:
    if not cfg.should_system:
        return None

    logger.info("📦 Preparing system provisioning...")
    
    connection = remote.ConnectionArgs(
        host=vps_ip,
        user=cfg.vps_user,
        agent_socket_path=os.environ.get("SSH_AUTH_SOCK")
    )

    script_content = cfg.bootstrap_script
    encoded_script = base64.b64encode(script_content.encode('utf-8')).decode('utf-8')

    # Restored your exact secure Base64 deployment logic
    install_cmd = (
        f"echo '{encoded_script}' | base64 -d > /tmp/install.sh && "
        f"chmod +x /tmp/install.sh && "
        f"sudo bash /tmp/install.sh vps"
    )

    return remote.Command("vps-bootstrap",
        connection=connection,
        create=install_cmd,
        # Added force_key to triggers to allow manual force re-run
        triggers=[script_content, cfg.force_key],
        opts=pulumi.ResourceOptions(depends_on=deps)
    )

# --- 4. Deployment Logic ---
def deploy_app(vps_ip: str, cfg: ArchitectConfig, dependency: Optional[pulumi.Resource]):
    if not cfg.should_deploy:
        return None

    logger.info("🚢 Deploying Application Stack...")

    # if force_reinstall
    reset_check = remote.Command("k3s-ready-check",
        connection=remote.ConnectionArgs(
            host=vps_ip,
            user=cfg.vps_user,
            agent_socket_path=os.environ.get("SSH_AUTH_SOCK")
        ),
        create="until [ -f /etc/rancher/k3s/k3s.yaml ]; do sleep 5; done && sudo chmod 644 /etc/rancher/k3s/k3s.yaml",
        triggers=[cfg.force_key],
        opts=pulumi.ResourceOptions(depends_on=[dependency] if dependency else [])
    )

    # 1. Retrieve Kubeconfig (Original SED logic preserved)
    kubeconfig_cmd = remote.Command("get-kubeconfig",
        connection=remote.ConnectionArgs(
            host=vps_ip,
            user=cfg.vps_user,
            agent_socket_path=os.environ.get("SSH_AUTH_SOCK")
        ),
        create=f"sudo cat /etc/rancher/k3s/k3s.yaml | sed 's/127.0.0.1/{vps_ip}/g'",
        triggers=[cfg.force_key], 
        opts=pulumi.ResourceOptions(depends_on=[reset_check])
    )

    # 2. K8s Provider
    k3s_provider = k8s.Provider("k3s-provider",
        kubeconfig=kubeconfig_cmd.stdout,
        enable_server_side_apply=True,
        delete_unreachable=True,
        kube_client_settings=k8s.KubeClientSettingsArgs(
            timeout=10
        ),
        opts=pulumi.ResourceOptions(
            depends_on=[kubeconfig_cmd],
            delete_before_replace=True 
        )
    )

    # 3. Helm Release (Restored FileAsset and exact paths)
    return k8s.helm.v3.Release("the-architect-release",
        k8s.helm.v3.ReleaseArgs(
            chart="../infra/charts/the-architect",
            namespace="agentic-architect",
            create_namespace=True,
            value_yaml_files=[
                pulumi.FileAsset("../infra/charts/the-architect/values.yaml"),
                pulumi.FileAsset("../infra/charts/the-architect/values-vps.yaml")
            ],
            values={
                "force_update": cfg.force_key, # Added to trigger Helm rollouts
                "ollama": {"image": "ghcr.io/fabienfrfr/custom-ollama-gemma:latest"},
                "architect": {"image": "ghcr.io/fabienfrfr/agentic-architect:latest"},
                "ingress": {"enabled": True, "host": "thearchitect.dev"}
            }
        ),
        opts=pulumi.ResourceOptions(
            provider=k3s_provider,
            replace_on_changes=["values"],
            delete_before_replace=True,
            retain_on_delete=True
        )
    )

# --- 5. Main Orchestration ---
def main():
    cfg = ArchitectConfig()
    infra_deps = []

    # Layer 1: Infrastructure (OVH)
    if cfg.should_infra:
        rebuild = VPSRebuild("vps-rebuild", {
            "endpoint": cfg.ovh_cfg.require("endpoint"),
            "ak": cfg.ovh_cfg.require("applicationKey"),
            "as_key": cfg.ovh_cfg.require_secret("applicationSecret"),
            "ck": cfg.ovh_cfg.require_secret("consumerKey"),
            "vps_name": cfg.vps_name,
            "version": cfg.ubuntu_version,
            "ssh_key": cfg.public_ssh_key,
            "force_trigger": cfg.force_key,
        }, opts=pulumi.ResourceOptions(
            replace_on_changes=["force_trigger"],
            delete_before_replace=True
            )
        )
        infra_deps.append(rebuild)

    # Layer 2: System (K3s/Tools)
    bootstrap_cmd = provision_system(cfg.vps_ip, cfg, infra_deps)

    # Layer 3: Application (Helm)
    app_release = deploy_app(cfg.vps_ip, cfg, bootstrap_cmd)

    # Exports (Original exports preserved)
    pulumi.export("vps_ip", cfg.vps_ip)
    pulumi.export("architect_status", "Online" if bootstrap_cmd else "Infrastructure Ready")
    pulumi.export("app_status", "Deployed")

if __name__ == "__main__":
    main()
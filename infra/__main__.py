import os
import json
from pathlib import Path
from typing import Optional, List

import base64

import pulumi
import pulumi_ovh as ovh
import pulumi_kubernetes as k8s
import pulumi_command as command
from pulumi_command import remote

import ovh as ovh_sdk

# --- 1. Configuration Manager ---

class ArchitectConfig:
    """Manages project configuration and local file parsing."""
    def __init__(self):
        self.config = pulumi.Config()
        self.ovh_config = pulumi.Config("ovh")
        self.vps_name: str = self.config.get("vps_name") or "vps-5dc72e2c.vps.ovh.net"
        self.vps_user: str = self.config.get("vps_user") or "ubuntu"
        self.domain: str = self.config.get("domain") or "thearchitect.dev"
        self.image: str = self.config.get("image_id") or "ubuntu2404_64"
        
        # Deployment Flags (Toggles)
        self.should_setup_infra: bool = self.config.get_bool("setup_infra") or False
        self.should_setup_system: bool = self.config.get_bool("setup_system") or False
        self.should_deploy_app: bool = self.config.get_bool("deploy_app") or False

        self.reinstall_force: str = self.config.get("reinstall_force") or "0"

    @property
    def public_key(self) -> str:
        path = Path.home() / ".ssh" / "id_rsa.pub"
        return path.read_text().strip()

    @property
    def bootstrap_script(self) -> str:
        path = Path(__file__).resolve().parent.parent / "scripts" / "install-tools.sh"
        return path.read_text()

# --- 2. Resource Modules ---

from pulumi.dynamic import Resource, ResourceProvider, CreateResult

# 1. Le "Moteur" de réinstallation
class OVHReinstallProvider(ResourceProvider):
    def create(self, props):
        client = ovh_sdk.Client(
            endpoint='ovh-eu',
            application_key=props['ak'],
            application_secret=props['as_key'],
            consumer_key=props['ck'],
        )
        # L'appel RÉEL à l'API
        client.post(f"/vps/{props['vps_name']}/reinstall", 
                    templateId=props['image'], 
                    sshKey=[props['ssh_key']])
        
        return CreateResult(id_="ovh-reinstall-id", outs=props)

# 2. La Ressource Pulumi
class OVHReinstall(Resource):
    def __init__(self, name, props, opts=None):
        super().__init__(OVHReinstallProvider(), name, props, opts)

# 3. La fonction de gestion révisée
def handle_vps_reinstall(cfg: ArchitectConfig) -> tuple[str, List[pulumi.Resource]]:
    vps_data = ovh.vps.get_vps(service_name=cfg.vps_name)
    vps_host = vps_data.service_name 
    deps = []

    if not cfg.should_setup_infra:
        return vps_host, deps

    # On crée la ressource de réinstallation
    reinstall = OVHReinstall("vps-reinstall-action", {
        "ak": cfg.ovh_config.get("applicationKey"),
        "as_key": cfg.ovh_config.require_secret("applicationSecret"),
        "ck": cfg.ovh_config.require_secret("consumerKey"),
        "vps_name": cfg.vps_name,
        "image": cfg.image,
        "ssh_key": cfg.public_key,
        "force": cfg.reinstall_force # Pour forcer le remplacement
    })
    deps.append(reinstall)

    # 4. L'attente de 3 minutes (BLOQUANTE)
    wait_ready = command.local.Command("wait-for-vps-reboot",
        create="sleep 180",
        opts=pulumi.ResourceOptions(depends_on=[reinstall])
    )
    deps.append(wait_ready)

    return vps_host, deps

def provision_system(vps_ip: pulumi.Output[str], cfg: ArchitectConfig, deps: List[pulumi.Resource]) -> Optional[remote.Command]:
    """Executes the bootstrap script on the remote host."""
    if not cfg.should_setup_system:
        return None

    connection = remote.ConnectionArgs(
        host=vps_ip,
        user=cfg.vps_user,
        agent_socket_path=os.environ.get("SSH_AUTH_SOCK")
    )

    script_content = cfg.bootstrap_script
    encoded_script = base64.b64encode(script_content.encode('utf-8')).decode('utf-8')

    install_cmd = (
        f"echo '{encoded_script}' | base64 -d > /tmp/install.sh && "
        f"chmod +x /tmp/install.sh && "
        f"bash /tmp/install.sh vps"
    )

    return remote.Command("vps-bootstrap",
        connection=connection,
        create=install_cmd,
        triggers=[script_content],
        opts=pulumi.ResourceOptions(depends_on=deps)
    )

def deploy_k8s_app(vps_ip: pulumi.Output[str], cfg: ArchitectConfig, dependency: Optional[pulumi.Resource]):
    """Retrieves kubeconfig and deploys the AgenticArchitect application."""
    if not cfg.should_deploy_app:
        return

    kubeconfig_cmd = remote.Command("get-kubeconfig",
        connection=remote.ConnectionArgs(
            host=vps_ip,
            user=cfg.vps_user,
            agent_socket_path=os.environ.get("SSH_AUTH_SOCK")
        ),
        create=f"sudo cat /etc/rancher/k3s/k3s.yaml | sed 's/127.0.0.1/{vps_ip}/g'",
        opts=pulumi.ResourceOptions(depends_on=[dependency] if dependency else [])
    )


    # 2. Configure K8s Provider
    k8s_provider = k8s.Provider("k3s-provider",
        kubeconfig=kubeconfig_cmd.stdout,
        opts=pulumi.ResourceOptions(depends_on=[kubeconfig_cmd])
    )

    # 3. Deploy Pods
    app_labels = {"app": "architect"}
    k8s.apps.v1.Deployment("architect-app",
        spec=k8s.apps.v1.DeploymentSpecArgs(
            selector=k8s.meta.v1.LabelSelectorArgs(match_labels=app_labels),
            template=k8s.core.v1.PodTemplateSpecArgs(
                metadata=k8s.meta.v1.ObjectMetaArgs(labels=app_labels),
                spec=k8s.core.v1.PodSpecArgs(
                    containers=[k8s.core.v1.ContainerArgs(
                        name="agentic-architect",
                        image="ghcr.io/fabienfrfr/agenticarchitect:latest",
                    )]
                )
            )
        ),
        opts=pulumi.ResourceOptions(provider=k8s_provider)
    )

# --- 3. Orchestration ---

def main():
    cfg = ArchitectConfig()
    
    # Layer 1: Infrastructure (Existing VPS + Reinstall)
    vps_ip, infra_deps = handle_vps_reinstall(cfg)
    
    # Layer 2: System Setup (k3s, docker, etc.)
    bootstrap_cmd = provision_system(vps_ip, cfg, infra_deps)
    
    # Layer 3: Application (K8s)
    deploy_k8s_app(vps_ip, cfg, bootstrap_cmd)

    # Exports
    pulumi.export("vps_ip", vps_ip)
    pulumi.export("endpoint", f"http://{cfg.domain}")

if __name__ == "__main__":
    main()
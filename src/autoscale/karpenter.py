
import yaml
from kubernetes import client, config as k8s_config

NODEPOOL_TEMPLATE = """
apiVersion: karpenter.sh/v1beta1
kind: NodePool
metadata:
  name: gpu-pool
spec:
  template:
    spec:
      requirements:
      - key: kubernetes.io/arch
        operator: In
        values: [amd64]
      - key: karpenter.sh/capacity-type
        operator: In
        values: [spot, on-demand]
      - key: node.kubernetes.io/instance-type
        operator: In
        values: [p3.2xlarge, p3.8xlarge, p3.16xlarge]
      nodeClassRef:
        apiVersion: karpenter.k8s.aws/v1beta1
        kind: EC2NodeClass
        name: gpu-node-class
  limits:
    cpu: 256
    memory: 1024Gi
  disruption:
    consolidationPolicy: WhenEmpty
    consolidateAfter: 30s
"""

def apply_nodepool(kubeconfig_path: str = None):
    if kubeconfig_path:
        k8s_config.load_kube_config(config_file=kubeconfig_path)
    else:
        k8s_config.load_incluster_config()
    manifest = yaml.safe_load(NODEPOOL_TEMPLATE)
    api = client.CustomObjectsApi()
    api.create_cluster_custom_object(
        group="karpenter.sh", version="v1beta1",
        plural="nodepools", body=manifest
    )
    print("GPU NodePool applied successfully")

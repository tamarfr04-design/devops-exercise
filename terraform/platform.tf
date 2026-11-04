resource "helm_release" "ingress_nginx" {
  name             = "ingress-nginx"
  repository       = "https://kubernetes.github.io/ingress-nginx"
  chart            = "ingress-nginx"
  namespace        = "ingress-nginx"
  create_namespace = true
  wait             = true

  values = [yamlencode({
    controller = {
      # Bind 80/443 directly on the node; kind maps them to the Mac.
      hostPort = { enabled = true }
      service  = { type = "NodePort" } # kind has no cloud load balancer
      # Run on the control-plane node, the only one with the port mappings.
      nodeSelector = {
        "kubernetes.io/hostname" = "${local.cluster_name}-control-plane"
      }
      tolerations = [{
        key      = "node-role.kubernetes.io/control-plane"
        operator = "Exists"
        effect   = "NoSchedule"
      }]
      ingressClassResource = { default = true }
    }
  })]

  depends_on = [kind_cluster.this]
}

resource "helm_release" "argocd" {
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  namespace        = "argocd"
  create_namespace = true
  wait             = true

  depends_on = [kind_cluster.this]
}
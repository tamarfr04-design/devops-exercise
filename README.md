# DevOps Exercise

## Plan
1. Tooling: Homebrew, Docker Desktop, kind, kubectl, Terraform, Helm, gh, VS Code
2. App: Python stdlib web service (`/` HTML page with message/version/pod, `/healthz`)
3. Dockerfile: slim Python image, non-root user (uid 10001)
4. Terraform: kind cluster (1 control-plane + 2 workers) + Argo CD + ingress-nginx via Helm
5. GitOps: Argo CD Application pointing at `k8s/` in this repo
6. CI: GitHub Actions builds the image, pushes to GHCR tagged with the commit SHA, commits the new tag to `k8s/`
7. Zero-downtime check: curl loop during rollout

## Decisions
- Public repo, so Argo CD can read it without credentials.
- kind for the local cluster: nodes run as Docker containers, so 1 control-plane + 2 workers is simple config, and there's a Terraform provider for it.
- ingress-nginx as the ingress controller: best-documented setup with kind, fastest under time pressure. Trade-off: the community project was retired in March 2026, so for production I'd use a maintained option (AWS Load Balancer Controller on EKS, Gateway API, or Traefik).
- The Argo CD Application is registered once with `kubectl apply` (bootstrap). After that, all changes go through git; CI never touches the cluster.

## Progress
- [ ] Part 0: setup, app, Dockerfile
- [ ] Part 1: Terraform cluster
- [ ] Part 2: GitOps deployment
- [ ] Part 3: CI/CD
- [x] Part 0: setup, app, Dockerfile
- [x] Part 1: Terraform cluster
- [x] Part 2: GitOps deployment

EOF
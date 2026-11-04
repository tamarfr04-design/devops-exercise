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
GHCR package is public, so the cluster needs no imagePullSecret. In production I’d keep it private and use pull credentials (or ECR with IAM on EKS).”


## Progress
- [ ] Part 0: setup, app, Dockerfile
- [ ] Part 1: Terraform cluster
- [ ] Part 2: GitOps deployment
- [ ] Part 3: CI/CD
- [x] Part 0: setup, app, Dockerfile
- [x] Part 1: Terraform cluster
- [x] Part 2: GitOps deployment
- [x] Part 3: CI/CD (build, push, tag bump)


## Zero-downtime test
`scripts/zero-downtime-check.sh` ran during the rollout from <old SHA> to <new SHA>: OK: ____  FAILED: 0.
What makes it work: maxUnavailable 0 / maxSurge 1, readiness probe, preStop sleep (endpoint removal before shutdown), graceful SIGTERM handling in the app.

## What I finished
- Part 0: Python stdlib web service (`/` HTML with message, version, pod name; `/healthz`), Dockerfile running as non-root (uid 10001)
- Part 1: Terraform creates a kind cluster (1 control-plane + 2 workers) and installs ingress-nginx and Argo CD with Helm
- Part 2: Argo CD syncs `k8s/` (kustomize): 2 replicas, readiness/liveness probes, requests/limits, Ingress at http://localhost
- Part 3: GitHub Actions builds a multi-arch image (amd64 + arm64), pushes to GHCR tagged with the commit SHA, commits the new tag to `k8s/kustomization.yaml`; Argo CD rolls it out. No kubectl from CI.
- Zero-downtime: `scripts/zero-downtime-check.sh` during the rollout from 3155ee3 to 7cf4c73: 1401 requests, 0 failed.

## What's missing
- The Argo CD Application is bootstrapped with one `kubectl apply`, not by Terraform, so after `terraform destroy` + `apply` it has to be applied again.
- Bonus items: HPA, Prometheus/Grafana.
- GitHub Actions versions should be bumped (Node 20 deprecation warning).

## One decision and why
Multi-arch image build in CI. The kind nodes on this Mac are arm64 and GitHub runners are amd64; an amd64-only image would crash on the cluster with `exec format error`. Building both platforms with QEMU + buildx makes the same tag work locally and on standard x86 servers.

## Where the AI was wrong
The AI suggested GitHub Actions versions (`actions/checkout@v4`, `docker/build-push-action@v6`, and others) that target the deprecated Node.js 20 runtime. I noticed it from the deprecation annotation on the first green CI run. It still works because GitHub forces Node 24, but the versions should be updated to the current majors.

## Running this on EKS in production
- Cluster: EKS created with Terraform (VPC module, managed node groups or Karpenter), remote state in S3 with locking, separate environments.
- Ingress: AWS Load Balancer Controller (ALB) with TLS from ACM, and ExternalDNS for Route 53 records.
- Images: private ECR with scanning; nodes pull via IAM. CI authenticates to AWS with GitHub OIDC (no long-lived keys).
- GitOps: Argo CD itself installed and managed via app-of-apps, SSO login, repo access with a deploy key or GitHub App, Application created by Terraform/app-of-apps, not kubectl.
- Reliability: HPA + Cluster Autoscaler/Karpenter, PodDisruptionBudget, topology spread across AZs.
- Security: secrets in AWS Secrets Manager via External Secrets, IRSA/Pod Identity for app permissions, NetworkPolicies, image signing.
- Observability: Prometheus/Grafana (or Amazon Managed Prometheus/Grafana), central logs, alerting.
- Promotion: dev → staging → prod by tag bumps in git, with PR review and protected `main`.
EOF

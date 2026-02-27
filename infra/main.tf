terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    # bucket and prefix configured via -backend-config flags or workspace
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "container.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "compute.googleapis.com",
    "dns.googleapis.com",
    "monitoring.googleapis.com",
  ])
  service            = each.key
  disable_on_destroy = false
}

# VPC
resource "google_compute_network" "vpc" {
  name                    = "${var.project_id}-vpc"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.apis]
}

# Subnet
resource "google_compute_subnetwork" "gke_subnet" {
  name          = "${var.project_id}-gke-subnet"
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.vpc.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = var.pods_cidr
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = var.services_cidr
  }

  private_ip_google_access = true
}

# Static IP for Cloud NAT egress
resource "google_compute_address" "nat_ip" {
  name   = "${var.project_id}-nat-ip"
  region = var.region
}

# Cloud Router
resource "google_compute_router" "router" {
  name    = "${var.project_id}-router"
  region  = var.region
  network = google_compute_network.vpc.id
}

# Cloud NAT
resource "google_compute_router_nat" "nat" {
  name                               = "${var.project_id}-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "MANUAL_ONLY"
  nat_ips                            = [google_compute_address.nat_ip.self_link]
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# GKE Autopilot Cluster
resource "google_container_cluster" "primary" {
  provider = google-beta
  name     = var.cluster_name
  location = var.region

  enable_autopilot = true

  network    = google_compute_network.vpc.id
  subnetwork = google_compute_subnetwork.gke_subnet.id

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = var.master_cidr
  }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  release_channel {
    channel = "REGULAR"
  }

  depends_on = [
    google_project_service.apis,
    google_compute_router_nat.nat,
  ]
}

# Artifact Registry
resource "google_artifact_registry_repository" "images" {
  repository_id = var.registry_name
  location      = var.region
  format        = "DOCKER"
  description   = "Travel AI container images"

  depends_on = [google_project_service.apis]
}

# DNS Zone
resource "google_dns_managed_zone" "travel_ai" {
  name        = replace(var.dns_zone_name, ".", "-")
  dns_name    = "${var.dns_zone_name}."
  description = "Travel AI DNS zone"

  depends_on = [google_project_service.apis]
}

# DNS A records per environment
resource "google_dns_record_set" "env_records" {
  for_each = toset(["dev", "staging", "preprod", "app"])

  name         = "${each.key}.${var.dns_zone_name}."
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.travel_ai.name
  rrdatas      = [var.ingress_ip]

  depends_on = [google_dns_managed_zone.travel_ai]
}

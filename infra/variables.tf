variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  default     = "travel-ai-cluster"
}

variable "registry_name" {
  description = "Artifact Registry repository name"
  type        = string
  default     = "travel-ai"
}

variable "subnet_cidr" {
  description = "GKE nodes subnet CIDR"
  type        = string
  default     = "10.0.0.0/20"
}

variable "pods_cidr" {
  description = "Pod IP range"
  type        = string
  default     = "10.4.0.0/14"
}

variable "services_cidr" {
  description = "Service IP range"
  type        = string
  default     = "10.8.0.0/20"
}

variable "master_cidr" {
  description = "GKE control-plane CIDR (/28)"
  type        = string
  default     = "172.16.0.0/28"
}

variable "dns_zone_name" {
  description = "Managed DNS zone domain (e.g. travel-ai.example.com)"
  type        = string
}

variable "ingress_ip" {
  description = "IP address for DNS A records (ingress-nginx LB IP)"
  type        = string
  default     = "0.0.0.0"
}

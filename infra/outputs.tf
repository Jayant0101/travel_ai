output "cluster_name" {
  value = google_container_cluster.primary.name
}

output "cluster_endpoint" {
  value     = google_container_cluster.primary.endpoint
  sensitive = true
}

output "registry_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${var.registry_name}"
}

output "nat_ip" {
  description = "Static egress IP for Cloud NAT (add to MongoDB Atlas allowlist)"
  value       = google_compute_address.nat_ip.address
}

output "dns_name_servers" {
  description = "Name servers for the DNS zone — configure these at your registrar"
  value       = google_dns_managed_zone.travel_ai.name_servers
}

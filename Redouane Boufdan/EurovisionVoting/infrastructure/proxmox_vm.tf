terraform {
  required_providers {
    proxmox = {
      source  = "Telmate/proxmox"
      version = ">= 3.0.1-rc1"
    }
  }
}

# Provider values are normally injected via environment variables or a tfvars file.
provider "proxmox" {}

resource "proxmox_vm_qemu" "eurovision_proxmox_worker" {
  name        = "eurovision-proxmox-worker"
  target_node = var.proxmox_node
  clone       = "ubuntu-template"
  cores       = 2
  memory      = 4096

  disk {
    slot = "scsi0"
    size = "30G"
    type = "disk"
    storage = "local-lvm"
  }
}

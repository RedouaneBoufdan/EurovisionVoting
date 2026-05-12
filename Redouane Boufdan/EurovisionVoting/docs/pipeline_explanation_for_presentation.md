# Pipeline explanation for oral presentation

## Step 1 Preparation
We check that the data exists, create folders and clean old result files.

## Step 2 Provisioning
We prepare VM infrastructure. The project contains Terraform examples for Proxmox and AWS.

## Step 3 Deployment
The application is packaged and prepared for deployment on the virtual machines.

## Step 3A Services
The project can run as Docker containers and also contains Kubernetes YAML files.

## Step 3B Streaming and Storage
Incoming votes are written to a stream file and to a storage file. This simulates a streaming system and persistent storage.

## Step 4 Voting simulation
The program generates realistic Eurovision votes with rush moments and country bias.

## Step 5 Results per datacenter
Votes are first counted per datacenter. This shows distributed processing.

## Step 6 Global results
The datacenter results are reduced into one global ranking.

## Step 7 Announce winners
The system writes the winner into `winner.txt`.

## Step 8 Stop all systems
The project writes a shutdown report and explains what must be stopped after the event.

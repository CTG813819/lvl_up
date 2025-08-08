# Quick AWS Deployment - Replace PC Backend

## Overview
This guide will help you deploy your AI Learning backend to AWS so it works without your PC connection.

## Prerequisites

### 1. **AWS Account Setup**
- Create AWS account at https://aws.amazon.com
- Set up billing (you'll need a credit card)
- Create an IAM user with EC2 permissions

### 2. **Install AWS CLI**
```bash
# Windows (using PowerShell)
winget install -e --id Amazon.AWSCLI

# Or download from: https://aws.amazon.com/cli/
```

### 3. **Configure AWS CLI**
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key  
# Enter your region (e.g., us-east-1)
# Enter output format (json)
```

## Step 1: Create EC2 Instance

### **Launch EC2 Instance**
1. Go to AWS Console → EC2 → Launch Instance
2. **Instance Type**: `t3.medium` (2 vCPU, 4GB RAM)
3. **AMI**: Ubuntu Server 22.04 LTS
4. **Storage**: 20GB GP3 SSD
5. **Security Group**: Create new with these rules:
   - SSH (22): Your IP only
   - HTTP (80): 0.0.0.0/0
   - HTTPS (443): 0.0.0.0/0
   - Custom TCP (4000): 0.0.0.0/0
6. **Key Pair**: Create new key pair and download `.pem` file

### **Get Your EC2 IP**
After launch, note your EC2 instance's **Public IPv4 address** (e.g., `3.250.123.45`)

## Step 2: Deploy Backend to AWS

### **Option A: Automated Deployment (Recommended)**
```bash
run_terminal_cmd 
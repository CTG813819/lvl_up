# AWS Deployment Setup Script
# This script helps you set up automated deployment to AWS

Write-Host "=== AWS Deployment Setup ===" -ForegroundColor Green
Write-Host ""

# Display the public key that needs to be added to AWS
Write-Host "1. PUBLIC KEY TO ADD TO AWS SERVER:" -ForegroundColor Yellow
Write-Host "Copy this entire line and add it to ~/.ssh/authorized_keys on your AWS server:"
Write-Host ""
$publicKey = Get-Content "C:\Users\Canice\.ssh\github_actions_deploy.pub"
Write-Host $publicKey -ForegroundColor Cyan
Write-Host ""

# Display the private key for GitHub secrets
Write-Host "2. PRIVATE KEY FOR GITHUB SECRETS:" -ForegroundColor Yellow
Write-Host "Copy this entire block (including the BEGIN and END lines) for the AWS_SSH_PRIVATE_KEY secret:"
Write-Host ""
$privateKey = Get-Content "C:\Users\Canice\.ssh\github_actions_deploy"
Write-Host $privateKey -ForegroundColor Cyan
Write-Host ""

# Instructions for AWS server setup
Write-Host "3. AWS SERVER SETUP COMMANDS:" -ForegroundColor Yellow
Write-Host "SSH into your AWS server and run these commands:"
Write-Host ""
Write-Host "ssh ubuntu@44.204.184.21" -ForegroundColor Cyan
Write-Host "echo '$publicKey' >> ~/.ssh/authorized_keys" -ForegroundColor Cyan
Write-Host "chmod 600 ~/.ssh/authorized_keys" -ForegroundColor Cyan
Write-Host ""

# Instructions for GitHub secrets
Write-Host "4. GITHUB SECRETS TO ADD:" -ForegroundColor Yellow
Write-Host "Go to your GitHub repo → Settings → Secrets and variables → Actions → New repository secret"
Write-Host "Add these secrets:"
Write-Host ""
Write-Host "AWS_SSH_PRIVATE_KEY: [The private key above]" -ForegroundColor Cyan
Write-Host "AWS_HOST: 44.204.184.21" -ForegroundColor Cyan
Write-Host "AWS_USER: ubuntu" -ForegroundColor Cyan
Write-Host ""

# Test SSH connection
Write-Host "5. TEST SSH CONNECTION:" -ForegroundColor Yellow
Write-Host "After adding the public key to AWS, test the connection:"
Write-Host ""
Write-Host "ssh -i C:\Users\Canice\.ssh\github_actions_deploy ubuntu@44.204.184.21" -ForegroundColor Cyan
Write-Host ""

Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host "After completing these steps, push your code to GitHub and the workflow will auto-deploy to AWS!" 
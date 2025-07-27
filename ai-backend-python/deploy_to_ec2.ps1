# Proposal Cleanup System - EC2 Deployment Script (PowerShell)
# ============================================================
# This script automates the deployment of the cleanup system to your EC2 instance

param(
    [string]$PemPath = "C:\projects\lvl_up\New.pem",
    [string]$EC2Host = "ec2-34-202-215-209.compute-1.amazonaws.com",
    [string]$EC2User = "ubuntu",
    [string]$RemotePath = "/home/ubuntu/ai-backend-python"
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

# Function to check if PEM file exists
function Test-PemFile {
    if (-not (Test-Path $PemPath)) {
        Write-Error "PEM file not found at: $PemPath"
        Write-Error "Please update the PemPath parameter or ensure the file exists"
        exit 1
    }
    Write-Success "PEM file found: $PemPath"
}

# Function to check if required files exist
function Test-RequiredFiles {
    $requiredFiles = @(
        "cleanup_all_pending_proposals.py",
        "deploy_cleanup.sh",
        "DEPLOYMENT_GUIDE.md"
    )
    
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path $file)) {
            Write-Error "Required file not found: $file"
            Write-Error "Please ensure all required files are in the current directory"
            exit 1
        }
    }
    
    Write-Success "All required files found"
}

# Function to deploy files to EC2
function Deploy-ToEC2 {
    Write-Status "Starting deployment to EC2..."
    
    $files = @(
        "cleanup_all_pending_proposals.py",
        "deploy_cleanup.sh", 
        "DEPLOYMENT_GUIDE.md"
    )
    
    foreach ($file in $files) {
        Write-Status "Deploying $file..."
        
        $scpCommand = "scp -i `"$PemPath`" $file ${EC2User}@${EC2Host}:${RemotePath}/"
        
        try {
            Invoke-Expression $scpCommand
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Successfully deployed $file"
            } else {
                Write-Error "Failed to deploy $file"
                return $false
            }
        }
        catch {
            Write-Error "Error deploying $file`: $_"
            return $false
        }
    }
    
    return $true
}

# Function to setup permissions on EC2
function Setup-EC2Permissions {
    Write-Status "Setting up permissions on EC2..."
    
    $sshCommand = "ssh -i `"$PemPath`" ${EC2User}@${EC2Host} `"cd $RemotePath && chmod +x deploy_cleanup.sh`"
    
    try {
        Invoke-Expression $sshCommand
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Successfully set permissions on EC2"
            return $true
        } else {
            Write-Error "Failed to set permissions on EC2"
            return $false
        }
    }
    catch {
        Write-Error "Error setting permissions on EC2: $_"
        return $false
    }
}

# Function to test connection to EC2
function Test-EC2Connection {
    Write-Status "Testing connection to EC2..."
    
    $sshCommand = "ssh -i `"$PemPath`" ${EC2User}@${EC2Host} `"echo 'Connection successful'`"
    
    try {
        Invoke-Expression $sshCommand
        if ($LASTEXITCODE -eq 0) {
            Write-Success "EC2 connection test successful"
            return $true
        } else {
            Write-Error "EC2 connection test failed"
            return $false
        }
    }
    catch {
        Write-Error "Error testing EC2 connection`: $_"
        return $false
    }
}

# Function to show next steps
function Show-NextSteps {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor $Green
    Write-Host "  DEPLOYMENT COMPLETED SUCCESSFULLY!" -ForegroundColor $Green
    Write-Host "==========================================" -ForegroundColor $Green
    Write-Host ""
    Write-Status "Next steps:"
    Write-Host "1. SSH into your EC2 instance:" -ForegroundColor $Blue
    Write-Host "   ssh -i `"$PemPath`" ${EC2User}@${EC2Host}" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "2. Navigate to the backend directory:" -ForegroundColor $Blue
    Write-Host "   cd $RemotePath" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "3. Run the cleanup system:" -ForegroundColor $Blue
    Write-Host "   ./deploy_cleanup.sh --verify-only     # Check current state" -ForegroundColor $Yellow
    Write-Host "   ./deploy_cleanup.sh --conservative    # Safe cleanup" -ForegroundColor $Yellow
    Write-Host "   ./deploy_cleanup.sh --aggressive      # Remove everything" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "4. For help and options:" -ForegroundColor $Blue
    Write-Host "   ./deploy_cleanup.sh --help" -ForegroundColor $Yellow
    Write-Host ""
    Write-Status "See DEPLOYMENT_GUIDE.md for detailed instructions"
}

# Main execution
function Main {
    Write-Host "==========================================" -ForegroundColor $Green
    Write-Host "  PROPOSAL CLEANUP SYSTEM DEPLOYMENT" -ForegroundColor $Green
    Write-Host "==========================================" -ForegroundColor $Green
    Write-Host ""
    
    # Pre-flight checks
    Write-Status "Performing pre-flight checks..."
    Test-PemFile
    Test-RequiredFiles
    
    # Test EC2 connection
    if (-not (Test-EC2Connection)) {
        Write-Error "Cannot connect to EC2. Please check your credentials and network connection."
        exit 1
    }
    
    # Deploy files
    if (-not (Deploy-ToEC2)) {
        Write-Error "Deployment failed. Please check the error messages above."
        exit 1
    }
    
    # Setup permissions
    if (-not (Setup-EC2Permissions)) {
        Write-Warning "Permission setup failed, but files were deployed."
        Write-Warning "You may need to manually set permissions on EC2."
    }
    
    # Show next steps
    Show-NextSteps
}

# Run main function
Main 
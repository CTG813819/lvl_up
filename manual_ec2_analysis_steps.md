# Manual EC2 Analysis Steps

## Step 1: Transfer the Analysis Script to EC2

Open PowerShell or Command Prompt and run:

```bash
# Transfer the comprehensive analysis script to EC2
scp -i "C:\projects\lvl_up\New.pem" comprehensive_system_analysis.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
```

## Step 2: SSH into EC2 and Run Analysis

```bash
# SSH into EC2
ssh -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com
```

Once connected to EC2, run these commands:

```bash
# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Check current directory and contents
pwd
ls -la

# Check Python version
python3 --version

# Install required packages (if needed)
pip3 install ast pathlib typing datetime importlib inspect

# Run the comprehensive analysis
python3 comprehensive_system_analysis.py

# Check for the generated report
ls -la *.json

# View the report (first 1000 characters)
head -c 1000 comprehensive_system_analysis_report.json
```

## Step 3: Download the Report (Optional)

To download the report to your local machine:

```bash
# From your local machine (new terminal)
scp -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/comprehensive_system_analysis_report.json ./
```

## What the Analysis Covers

The comprehensive analysis script will scan:

### Frontend (Flutter/Dart):
- ✅ All `.dart` files in `/lib` directory
- ✅ Functions, classes, and data structures
- ✅ AI-related functions and components
- ✅ Services, providers, widgets, and models
- ✅ Import statements and dependencies

### Backend (Python):
- ✅ All `.py` files in `/ai-backend-python` directory
- ✅ Functions, classes, and data structures
- ✅ AI-related functions and components
- ✅ FastAPI endpoints and routers
- ✅ Services, models, and database schemas
- ✅ Import statements and dependencies

### Integration Analysis:
- ✅ API endpoints vs frontend API calls
- ✅ Shared data models between frontend and backend
- ✅ Potential integration issues

### Output:
- 📊 Comprehensive JSON report with detailed analysis
- 📋 Summary statistics and key findings
- 🔍 Detailed breakdown of all components

## Expected Output

The script will generate a detailed report showing:
- Total files and lines of code analyzed
- Number of AI functions found
- API endpoints and their usage
- Service architecture overview
- Integration points between frontend and backend
- Key findings and potential issues

## Troubleshooting

If you encounter issues:

1. **Permission denied**: Make sure the PEM file has correct permissions
2. **Python not found**: Use `python3` instead of `python`
3. **Missing packages**: Install required packages with `pip3 install`
4. **Path issues**: Make sure you're in the correct directory on EC2

## Quick Commands

For quick execution, you can run the automated scripts:

**PowerShell:**
```powershell
.\deploy_analysis_to_ec2.ps1
```

**Bash (if using Git Bash or WSL):**
```bash
./deploy_analysis_to_ec2.sh
``` 
import subprocess
import os

def main():
    print("🚀 Deploying EC2 Fix Script...")
    print("=" * 40)
    
    # Check if we have the fix script
    if not os.path.exists('ec2_ssh_fix_script.sh'):
        print("❌ ec2_ssh_fix_script.sh not found!")
        return
    
    print("📋 Instructions to fix your EC2 backend:")
    print("")
    print("1️⃣ Copy the fix script to your EC2 instance:")
    print("   scp ec2_ssh_fix_script.sh ubuntu@34.202.215.209:~/")
    print("")
    print("2️⃣ SSH into your EC2 instance:")
    print("   ssh ubuntu@34.202.215.209")
    print("")
    print("3️⃣ Make the script executable and run it:")
    print("   chmod +x ~/ec2_ssh_fix_script.sh")
    print("   ~/ec2_ssh_fix_script.sh")
    print("")
    print("4️⃣ After the script completes, test your Flutter app")
    print("")
    print("🔧 What the script will do:")
    print("   • Stop the conflicting ai-backend-python service")
    print("   • Initialize the database")
    print("   • Add WebSocket support")
    print("   • Add missing API endpoints")
    print("   • Restart the imperium-monitoring service")
    print("   • Test all fixes")
    print("")
    print("⚠️  If you don't have SSH access, you'll need to:")
    print("   • Use your EC2 console to access the instance")
    print("   • Or provide SSH credentials to run this automatically")
    
    # Try to copy the script if we have SSH access
    try:
        print("\n🔄 Attempting to copy script automatically...")
        result = subprocess.run([
            'scp', 'ec2_ssh_fix_script.sh', 'ubuntu@34.202.215.209:~/'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Script copied successfully!")
            print("Now SSH into your EC2 instance and run:")
            print("   chmod +x ~/ec2_ssh_fix_script.sh")
            print("   ~/ec2_ssh_fix_script.sh")
        else:
            print("❌ Could not copy script automatically:")
            print(result.stderr)
            print("\nPlease copy it manually using the instructions above.")
    except FileNotFoundError:
        print("❌ scp command not found. Please copy the script manually.")
    except Exception as e:
        print(f"❌ Error copying script: {e}")
        print("Please copy it manually using the instructions above.")

if __name__ == '__main__':
    main() 
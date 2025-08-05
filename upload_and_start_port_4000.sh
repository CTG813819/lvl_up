#!/bin/bash

# Upload and Start Port 4000 Service
echo "📤 Uploading port 4000 service starter..."

# Upload the script
scp start_port_4000_service.py ubuntu@your-ec2-ip:/home/ubuntu/

echo "✅ Upload complete!"
echo ""
echo "🚀 Next steps on EC2:"
echo "1. Run the port 4000 starter: python3 start_port_4000_service.py"
echo "2. Test port 4000: curl http://localhost:4000/health"
echo "3. Run your comprehensive test again: python3 comprehensive_system_test.py"
echo ""
echo "💡 This will start the monitoring service on port 4000 and open the firewall." 
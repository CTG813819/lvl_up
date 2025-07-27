#!/usr/bin/env python3
"""
Fix database connection issues
"""

import os
import subprocess
import re

def fix_database_connection():
    """Fix database connection issues"""
    print("🔧 Fixing database connection...")
    
    # Check database configuration
    print("\n1. Checking database configuration...")
    
    config_file = "app/core/config.py"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            content = f.read()
            print("Database configuration found in config.py")
            
            # Look for DATABASE_URL
            db_url_match = re.search(r'DATABASE_URL\s*=\s*["\']([^"\']+)["\']', content)
            if db_url_match:
                db_url = db_url_match.group(1)
                print(f"Found DATABASE_URL: {db_url}")
                
                # Extract database name
                db_name_match = re.search(r'/([^/?]+)(?:\?|$)', db_url)
                if db_name_match:
                    db_name = db_name_match.group(1)
                    print(f"Database name: {db_name}")
                    
                    # Extract username
                    user_match = re.search(r'://([^:]+):', db_url)
                    if user_match:
                        username = user_match.group(1)
                        print(f"Username: {username}")
                        
                        # Create the database and user
                        print(f"\n2. Creating database and user...")
                        create_db_commands = f"""
# Run these commands to create the database and user:
sudo -u postgres psql << 'EOF'
CREATE USER {username} WITH PASSWORD 'your_password';
CREATE DATABASE {db_name} OWNER {username};
GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {username};
\q
EOF

# Then run the SQL script:
sudo -u postgres psql -d {db_name} -f create_json_function.sql

# Test the function:
sudo -u postgres psql -d {db_name} -c "SELECT json_extract_path_text('{{\\"test\\": \\"value\\"}}'::jsonb, 'test');"
"""
                        print(create_db_commands)
                        
                        # Write the commands to a file
                        with open('setup_database.sh', 'w') as f:
                            f.write(f"""#!/bin/bash
# Database setup script
echo "Setting up database..."

# Create user and database
sudo -u postgres psql << 'EOF'
CREATE USER {username} WITH PASSWORD 'your_password';
CREATE DATABASE {db_name} OWNER {username};
GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {username};
\q
EOF

# Run the SQL script
sudo -u postgres psql -d {db_name} -f create_json_function.sql

# Test the function
sudo -u postgres psql -d {db_name} -c "SELECT json_extract_path_text('{{\\"test\\": \\"value\\"}}'::jsonb, 'test');"

echo "Database setup completed!"
""")
                        
                        os.chmod('setup_database.sh', 0o755)
                        print(f"✅ Created setup_database.sh script")
                        print(f"Run: ./setup_database.sh")
                        
                        return db_name, username
                    else:
                        print("❌ Could not extract username from DATABASE_URL")
                else:
                    print("❌ Could not extract database name from DATABASE_URL")
            else:
                print("❌ DATABASE_URL not found in config.py")
    else:
        print("❌ config.py not found")
    
    # Check for .env file
    env_file = ".env"
    if os.path.exists(env_file):
        print("\nChecking .env file...")
        with open(env_file, 'r') as f:
            content = f.read()
            db_url_match = re.search(r'DATABASE_URL\s*=\s*([^\s]+)', content)
            if db_url_match:
                db_url = db_url_match.group(1)
                print(f"Found DATABASE_URL in .env: {db_url}")
    
    print("\n📝 Manual steps to fix database connection:")
    print("1. Connect as postgres superuser: sudo -u postgres psql")
    print("2. Create user: CREATE USER ubuntu WITH PASSWORD 'your_password';")
    print("3. Create database: CREATE DATABASE ai_backend OWNER ubuntu;")
    print("4. Grant privileges: GRANT ALL PRIVILEGES ON DATABASE ai_backend TO ubuntu;")
    print("5. Exit: \\q")
    print("6. Run SQL script: sudo -u postgres psql -d ai_backend -f create_json_function.sql")

if __name__ == "__main__":
    fix_database_connection() 
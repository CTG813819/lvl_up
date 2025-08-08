import requests
import json

# First, let's get the list of extensions to see what's available
def list_extensions():
    url = "http://34.202.215.209:4000/api/terra/extensions"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            extensions = response.json()
            print(f"Found {len(extensions)} extensions:")
            for ext in extensions:
                print(f"  - ID: {ext['id']}")
                print(f"    Title: {ext['menu_title']}")
                print(f"    Status: {ext['status']}")
                print()
            return extensions
        else:
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"Exception: {e}")
        return []

# Test delete functionality
def test_delete_extension(extension_id):
    url = f"http://34.202.215.209:4000/api/terra/extensions/{extension_id}"
    try:
        print(f"Attempting to delete extension {extension_id}...")
        response = requests.delete(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Extension deleted successfully!")
        else:
            print("❌ ERROR: Failed to delete extension")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    print("Testing Terra Extensions Delete Functionality")
    print("=" * 50)
    
    # List current extensions
    extensions = list_extensions()
    
    if extensions:
        # Ask user which extension to delete
        print("Available extensions for deletion:")
        for i, ext in enumerate(extensions):
            print(f"{i+1}. {ext['menu_title']} (ID: {ext['id']})")
        
        try:
            choice = int(input("\nEnter the number of the extension to delete (or 0 to cancel): "))
            if choice > 0 and choice <= len(extensions):
                selected_extension = extensions[choice-1]
                confirm = input(f"Are you sure you want to delete '{selected_extension['menu_title']}'? (y/N): ")
                if confirm.lower() == 'y':
                    test_delete_extension(selected_extension['id'])
                else:
                    print("Deletion cancelled.")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")
    else:
        print("No extensions found to delete.") 
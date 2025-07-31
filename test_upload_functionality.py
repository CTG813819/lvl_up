#!/usr/bin/env python3
"""
Test Upload Functionality
Test that the backend can receive uploads from Book of Lorgar and Oath Papers
"""

import aiohttp
import asyncio
import json
from datetime import datetime

class UploadTester:
    def __init__(self):
        self.base_url = "http://34.202.215.209:8000"
        self.test_results = {
            "backend_connectivity": False,
            "book_of_lorgar_upload": False,
            "oath_papers_upload": False,
            "learning_data_endpoint": False,
            "oath_papers_endpoint": False,
            "errors": []
        }

    async def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        print("🔍 Testing backend connectivity...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/health", timeout=10) as response:
                    if response.status == 200:
                        print("✅ Backend is accessible")
                        self.test_results["backend_connectivity"] = True
                        return True
                    else:
                        print(f"❌ Backend returned status {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Backend connectivity failed: {str(e)}")
            self.test_results["errors"].append(f"Backend connectivity: {str(e)}")
            return False

    async def test_learning_data_endpoint(self):
        """Test the learning data endpoint used by Book of Lorgar"""
        print("📚 Testing learning data endpoint...")
        try:
            test_data = {
                "title": "Test Knowledge",
                "subject": "Python Testing",
                "description": "This is a test upload from Book of Lorgar",
                "code": "print('Hello, World!')",
                "timestamp": datetime.now().isoformat()
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/learning/data",
                    json=test_data,
                    timeout=15
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ Learning data endpoint working")
                        print(f"   Response: {data}")
                        self.test_results["learning_data_endpoint"] = True
                        return True
                    else:
                        print(f"❌ Learning data endpoint failed: {response.status}")
                        error_text = await response.text()
                        print(f"   Error: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ Learning data endpoint error: {str(e)}")
            self.test_results["errors"].append(f"Learning data endpoint: {str(e)}")
            return False

    async def test_oath_papers_endpoint(self):
        """Test the oath papers endpoint"""
        print("📜 Testing oath papers endpoint...")
        try:
            test_data = {
                "subject": "Test Oath Paper",
                "tags": ["test", "python", "backend"],
                "description": "This is a test oath paper for AI learning",
                "code": "def test_function():\n    return 'test'",
                "targetAI": "Imperium",
                "aiWeights": {
                    "Imperium": 0.4,
                    "Sandbox": 0.3,
                    "Guardian": 0.2,
                    "Conquest": 0.1
                },
                "timestamp": datetime.now().isoformat(),
                "learningMode": "enhanced",
                "extractKeywords": True,
                "internetSearch": True,
                "gitIntegration": True
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/oath-papers",
                    json=test_data,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ Oath papers endpoint working")
                        print(f"   Response: {data}")
                        self.test_results["oath_papers_endpoint"] = True
                        return True
                    else:
                        print(f"❌ Oath papers endpoint failed: {response.status}")
                        error_text = await response.text()
                        print(f"   Error: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ Oath papers endpoint error: {str(e)}")
            self.test_results["errors"].append(f"Oath papers endpoint: {str(e)}")
            return False

    async def test_book_of_lorgar_upload(self):
        """Test Book of Lorgar upload functionality"""
        print("📖 Testing Book of Lorgar upload...")
        try:
            # Test the research functionality
            research_data = {
                "subject": "machine learning",
                "context": "Testing AI research capabilities"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/learning/data",
                    json=research_data,
                    timeout=20
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ Book of Lorgar research working")
                        print(f"   Research result: {data}")
                        self.test_results["book_of_lorgar_upload"] = True
                        return True
                    else:
                        print(f"❌ Book of Lorgar research failed: {response.status}")
                        error_text = await response.text()
                        print(f"   Error: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ Book of Lorgar upload error: {str(e)}")
            self.test_results["errors"].append(f"Book of Lorgar upload: {str(e)}")
            return False

    async def test_oath_papers_upload(self):
        """Test Oath Papers upload functionality"""
        print("📜 Testing Oath Papers upload...")
        try:
            oath_data = {
                "subject": "Advanced AI Testing",
                "tags": ["ai", "testing", "backend"],
                "description": "Testing oath paper upload functionality",
                "code": "class AITester:\n    def test_upload(self):\n        return 'success'",
                "targetAI": "Sandbox",
                "aiWeights": {
                    "Imperium": 0.3,
                    "Sandbox": 0.4,
                    "Guardian": 0.2,
                    "Conquest": 0.1
                },
                "timestamp": datetime.now().isoformat(),
                "learningMode": "enhanced",
                "extractKeywords": True,
                "internetSearch": True,
                "gitIntegration": True,
                "learningInstructions": {
                    "scanDescription": True,
                    "scanCode": True,
                    "extractKeywords": True,
                    "searchInternet": True,
                    "learnFromResults": True,
                    "updateCapabilities": True,
                    "pushToGit": True
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/oath-papers",
                    json=oath_data,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ Oath Papers upload working")
                        print(f"   Upload result: {data}")
                        self.test_results["oath_papers_upload"] = True
                        return True
                    else:
                        print(f"❌ Oath Papers upload failed: {response.status}")
                        error_text = await response.text()
                        print(f"   Error: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ Oath Papers upload error: {str(e)}")
            self.test_results["errors"].append(f"Oath Papers upload: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all upload functionality tests"""
        print("🚀 Starting Upload Functionality Tests...")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print("=" * 60)

        # Test 1: Backend connectivity
        if not await self.test_backend_connectivity():
            print("❌ Backend not accessible - skipping other tests")
            return

        # Test 2: Learning data endpoint
        await self.test_learning_data_endpoint()

        # Test 3: Oath papers endpoint
        await self.test_oath_papers_endpoint()

        # Test 4: Book of Lorgar upload
        await self.test_book_of_lorgar_upload()

        # Test 5: Oath Papers upload
        await self.test_oath_papers_upload()

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 UPLOAD FUNCTIONALITY TEST SUMMARY")
        print("=" * 60)

        print(f"🔗 Backend Connectivity: {'✅ Working' if self.test_results['backend_connectivity'] else '❌ Failed'}")
        print(f"📚 Learning Data Endpoint: {'✅ Working' if self.test_results['learning_data_endpoint'] else '❌ Failed'}")
        print(f"📜 Oath Papers Endpoint: {'✅ Working' if self.test_results['oath_papers_endpoint'] else '❌ Failed'}")
        print(f"📖 Book of Lorgar Upload: {'✅ Working' if self.test_results['book_of_lorgar_upload'] else '❌ Failed'}")
        print(f"📜 Oath Papers Upload: {'✅ Working' if self.test_results['oath_papers_upload'] else '❌ Failed'}")

        if self.test_results["errors"]:
            print(f"\n❌ Errors Found ({len(self.test_results['errors'])}):")
            for error in self.test_results["errors"]:
                print(f"   • {error}")

        working_count = sum([
            self.test_results["backend_connectivity"],
            self.test_results["learning_data_endpoint"],
            self.test_results["oath_papers_endpoint"],
            self.test_results["book_of_lorgar_upload"],
            self.test_results["oath_papers_upload"]
        ])

        total_tests = 5
        success_rate = (working_count / total_tests) * 100

        print(f"\n📈 Success Rate: {success_rate:.1f}% ({working_count}/{total_tests})")

        if success_rate == 100:
            print("🎉 All upload functionality tests passed!")
            print("✅ Book of Lorgar and Oath Papers should work correctly")
        elif success_rate >= 80:
            print("⚠️ Most tests passed - some functionality may be limited")
        else:
            print("❌ Multiple tests failed - upload functionality needs attention")

        # Save detailed results
        with open('upload_functionality_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: upload_functionality_test_results.json")

async def main():
    tester = UploadTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 
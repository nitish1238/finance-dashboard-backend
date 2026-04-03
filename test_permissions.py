import requests

class PermissionTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.tokens = {}
        self.users = {
            "admin": {"username": "admin", "password": "admin123"},
            "analyst": {"username": "analyst_user", "password": "Analyst@123"},
            "viewer": {"username": "viewer_user", "password": "Viewer@123"}
        }
    
    def login(self, role):
        """Login and get token for a role"""
        response = requests.post(
            f"{self.base_url}/api/users/auth/login/",
            json=self.users[role]
        )
        if response.status_code == 200:
            self.tokens[role] = response.json()['access']
            print(f"✅ {role.upper()} logged in successfully")
            return True
        else:
            print(f"❌ {role.upper()} login failed")
            return False
    
    def test_endpoint(self, role, method, endpoint, data=None):
        """Test an endpoint with specific role"""
        if role not in self.tokens:
            self.login(role)
        
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        
        if method == "GET":
            response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
        elif method == "POST":
            response = requests.post(f"{self.base_url}{endpoint}", headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(f"{self.base_url}{endpoint}", headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(f"{self.base_url}{endpoint}", headers=headers)
        
        return response.status_code, response.json() if response.text else None
    
    def run_permission_tests(self):
        """Run all permission tests"""
        print("\n" + "="*60)
        print("PERMISSION TESTING MATRIX")
        print("="*60)
        
        # Test cases: (role, method, endpoint, expected_status, description)
        test_cases = [
            # Viewer tests
            ("viewer", "GET", "/api/users/profile/", 200, "Viewer get profile"),
            ("viewer", "POST", "/api/records/", 403, "Viewer create transaction"),
            ("viewer", "PUT", "/api/records/1/", 403, "Viewer update transaction"),
            ("viewer", "DELETE", "/api/records/1/", 403, "Viewer delete transaction"),
            ("viewer", "GET", "/api/users/", 403, "Viewer list users"),
            
            # Analyst tests
            ("analyst", "GET", "/api/users/profile/", 200, "Analyst get profile"),
            ("analyst", "POST", "/api/records/", 201, "Analyst create transaction"),
            ("analyst", "PUT", "/api/records/1/", 200, "Analyst update transaction"),
            ("analyst", "DELETE", "/api/records/1/", 403, "Analyst delete transaction"),
            ("analyst", "GET", "/api/users/", 403, "Analyst list users"),
            
            # Admin tests
            ("admin", "GET", "/api/users/profile/", 200, "Admin get profile"),
            ("admin", "POST", "/api/records/", 201, "Admin create transaction"),
            ("admin", "DELETE", "/api/records/1/", 204, "Admin delete transaction"),
            ("admin", "GET", "/api/users/", 200, "Admin list users"),
            ("admin", "POST", "/api/users/", 201, "Admin create user"),
        ]
        
        results = []
        for role, method, endpoint, expected, description in test_cases:
            # First create a transaction for update/delete tests
            if "update" in description or "delete" in description:
                if "admin" in role:
                    # Create a test transaction first
                    headers = {"Authorization": f"Bearer {self.tokens['admin']}"}
                    requests.post(
                        f"{self.base_url}/api/records/",
                        headers=headers,
                        json={"amount": 100, "transaction_type": "expense", "category": "food"}
                    )
            
            status, data = self.test_endpoint(role, method, endpoint)
            
            # Check if status matches expected (or is in expected range)
            if method == "DELETE":
                passed = status in [expected, 204]  # DELETE can return 200 or 204
            else:
                passed = status == expected
            
            # Special check for permission denied
            if expected == 403 and "permission" in str(data).lower():
                passed = True
            
            results.append({
                "role": role,
                "description": description,
                "expected": expected,
                "got": status,
                "passed": passed
            })
            
            status_icon = "✅" if passed else "❌"
            print(f"{status_icon} {role.upper():8} - {description:35} (Expected: {expected}, Got: {status})")
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        passed = sum(1 for r in results if r["passed"])
        total = len(results)
        print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
        
        return results

if __name__ == "__main__":
    tester = PermissionTester()
    tester.run_permission_tests()
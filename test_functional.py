import unittest
from app import app

class TestBankingSystem(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_login_valid(self):
        # Test valid login
        response = self.app.post("/authenticate", data={
            "username": "user1",
            "password": "password1"
        })
        self.assertEqual(response.status_code, 302)  # Redirect to MFA page

    def test_login_invalid(self):
        # Test invalid login
        response = self.app.post("/authenticate", data={
            "username": "user1",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertIn(b"Invalid credentials", response.data)

    def test_fund_transfer_sufficient_balance(self):
        # Test fund transfer with sufficient balance
        with self.app as client:
            # Log in first
            client.post("/authenticate", data={
                "username": "user1",
                "password": "password1"
            })
            client.post("/mfa/user1", data={
                "mfa_code": "123456"
            })
            # Perform transfer
            response = client.post("/transfer/user1", data={
                "recipient": "user2",
                "amount": "100"
            })
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Transfer successful", response.data)

    def test_fund_transfer_insufficient_balance(self):
        # Test fund transfer with insufficient balance
        with self.app as client:
            # Log in first
            client.post("/authenticate", data={
                "username": "user1",
                "password": "password1"
            })
            client.post("/mfa/user1", data={
                "mfa_code": "123456"
            })
            # Perform transfer
            response = client.post("/transfer/user1", data={
                "recipient": "user2",
                "amount": "10000"  # More than balance
            })
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Invalid transfer amount", response.data)

if __name__ == "__main__":
    unittest.main()
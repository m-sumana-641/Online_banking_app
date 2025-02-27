from locust import HttpUser, task, between

class BankingUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def login(self):
        self.client.post("/authenticate", data={
            "username": "user1",
            "password": "password1"
        })

    @task(3)
    def dashboard(self):
        self.client.get("/dashboard/user1")

    @task(2)
    def transfer_funds(self):
        self.client.post("/transfer/user1", data={
            "recipient": "user2",
            "amount": "100"
        })

    @task(1)
    def pay_bills(self):
        self.client.post("/bill_payment/user1", data={
            "bill_type": "electricity",
            "amount": "50"
        })

    @task(1)
    def view_transactions(self):
        self.client.get("/transactions/user1")
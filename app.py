from flask import Flask, session, render_template, request, redirect, url_for
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey123'  # Set a secret key for session management

# Set session lifetime to 5 minutes
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

# Ensure sessions are marked as permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

# Disable HttpOnly and Secure flags for session cookie
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True

# Dummy user data for login
users = {
    "user1": "password1",
    "user2": "password2"
}

# Dummy account balance
account_balance = {
    "user1": 1000,
    "user2": 500
}

# Dummy MFA codes (for demonstration)
mfa_codes = {
    "user1": "123456",
    "user2": "654321"
}

# Dummy transaction history
transaction_history = {
    "user1": [
        {"type": "Transfer", "amount": -100, "recipient": "user2", "date": "2023-10-01"},
        {"type": "Bill Payment", "amount": -50, "bill_type": "Electricity", "date": "2023-10-02"}
    ],
    "user2": [
        {"type": "Transfer", "amount": 100, "sender": "user1", "date": "2023-10-01"}
    ]
}

@app.route("/")
def login():
    return render_template("login.html", error=None)

@app.route("/authenticate", methods=["POST"])
def authenticate():
    print(f"Full form data: {request.form}")  # Debugging

    username = request.form.get("username")
    password = request.form.get("password")

    print(f"Username: {username}, Password: {password}")

    if username in users and users[username] == password:
        session['username'] = username  # Store username in session
        print(f"Session set for user: {username}")  # Debugging
        return redirect(url_for("mfa", username=username))
    else:
        return render_template("login.html", error="Invalid credentials. Please try again.")

@app.route("/mfa/<username>", methods=["GET", "POST"])
def mfa(username):
    if request.method == "POST":
        mfa_code = request.form.get("mfa_code")

        # Debug print to check MFA code
        print(f"MFA Code Entered: {mfa_code}")

        if mfa_code == mfa_codes.get(username):
            session['username'] = username  # Ensure session is set
            return redirect(url_for("dashboard", username=username))
        else:
            return render_template("mfa.html", username=username, error="Invalid MFA code. Please try again.")

    return render_template("mfa.html", username=username)

@app.route("/dashboard/<username>")
def dashboard(username):
    # Ensure the user is logged in
    if 'username' not in session or session['username'] != username:
        return redirect(url_for("login"))

    balance = account_balance.get(username, 0)
    return render_template("dashboard.html", username=username, balance=balance)

@app.route("/account/<username>")
def account(username):
    # Ensure the user is logged in
    if 'username' not in session or session['username'] != username:
        return redirect(url_for("login"))

    # Dummy account details
    account_details = {
        "account_number": "123456789",
        "account_type": "Savings",
        "balance": account_balance.get(username, 0)
    }
    return render_template("account.html", username=username, account_details=account_details)

@app.route("/transfer/<username>", methods=["GET", "POST"])
def transfer(username):
    # Ensure the user is logged in
    if 'username' not in session or session['username'] != username:
        return redirect(url_for("login"))

    if request.method == "POST":
        amount = float(request.form.get("amount"))
        recipient = request.form.get("recipient")

        if amount > 0 and amount <= account_balance[username]:
            account_balance[username] -= amount
            account_balance[recipient] += amount
            # Add transaction to history
            transaction_history[username].append({
                "type": "Transfer",
                "amount": -amount,
                "recipient": recipient,
                "date": "2023-10-03"  # Use current date in a real application
            })
            transaction_history[recipient].append({
                "type": "Transfer",
                "amount": amount,
                "sender": username,
                "date": "2023-10-03"
            })
            return render_template("transaction_confirmation.html", 
                                 message=f"Transfer successful! New balance: ${account_balance[username]}",
                                 username=username)
        else:
            return render_template("transaction_confirmation.html", 
                                 message="Invalid transfer amount or insufficient balance.",
                                 username=username)

    return render_template("transfer.html", username=username)

@app.route("/bill_payment/<username>", methods=["GET", "POST"])
def bill_payment(username):
    # Ensure the user is logged in
    if 'username' not in session or session['username'] != username:
        return redirect(url_for("login"))

    if request.method == "POST":
        amount = float(request.form.get("amount"))
        bill_type = request.form.get("bill_type")

        if amount > 0 and amount <= account_balance[username]:
            account_balance[username] -= amount
            # Add transaction to history
            transaction_history[username].append({
                "type": "Bill Payment",
                "amount": -amount,
                "bill_type": bill_type,
                "date": "2023-10-03"  # Use current date in a real application
            })
            return render_template("transaction_confirmation.html", 
                                 message=f"Bill payment successful! New balance: ${account_balance[username]}",
                                 username=username)
        else:
            return render_template("transaction_confirmation.html", 
                                 message="Invalid payment amount or insufficient balance.",
                                 username=username)

    return render_template("bill_payment.html", username=username)

@app.route("/loan/<username>", methods=["GET", "POST"])
def loan(username):
    # Ensure the user is logged in
    if 'username' not in session or session['username'] != username:
        return redirect(url_for("login"))

    if request.method == "POST":
        loan_amount = float(request.form.get("loan_amount"))
        # Dummy loan approval logic
        if loan_amount > 0 and loan_amount <= 10000:
            return render_template("loan_confirmation.html", 
                                 message=f"Loan application for ${loan_amount} submitted successfully!",
                                 username=username)
        else:
            return render_template("loan_confirmation.html", 
                                 message="Invalid loan amount. Please enter an amount between $1 and $10,000.",
                                 username=username)

    return render_template("loan.html", username=username)

@app.route("/transactions/<username>")
def transactions(username):
    # Ensure the user is logged in
    if 'username' not in session or session['username'] != username:
        return redirect(url_for("login"))

    print(f"Session username: {session.get('username')}")
    return render_template("transactions.html", username=username, transactions=transaction_history.get(username, []))

if __name__ == "__main__":
    app.run(debug=True)
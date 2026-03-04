# 🛒 Retail Wizard: Advanced POS & Inventory Management System

Retail Wizard is a comprehensive, full-stack Point of Sale (POS) and inventory management web application. Designed for real-world retail environments, it handles secure cashier shifts, dynamic checkout workflows, location-based delivery logistics, and automated invoice generation. 

This project demonstrates practical implementations of Role-Based Access Control (RBAC), cryptographic security, relational database design, and real-time frontend calculations.

---

## ✨ Core Features

### 🔐 Security & Access Control
* **Role-Based Access (RBAC):** Distinct dashboards and permissions for `Admin` and `Cashier` roles.
* **Admin Approval Pipeline:** New user registrations are securely vaulted in a "pending" state until an Admin reviews and approves them.
* **Cryptographic Hashing:** All passwords are mathematically secured using `bcrypt` with a high-iteration work factor (14 rounds).
* **Strict Password Enforcement:** System strictly requires complex passwords (min. 8 characters, alphanumeric + symbols).

### 💳 Dynamic Point of Sale (POS)
* **Real-Time Cart Engine:** JavaScript-driven checkout that instantly calculates subtotals, complex discount layering, and exact change without refreshing the page.
* **Delivery Logistics Integration:** Selectable delivery PIN codes that dynamically reveal address fields and inject location-specific delivery fees into the final bill.
* **Advanced Coupon Logic:** Supports both flat-rate and percentage-based discounts with strict database-enforced usage limits.

### 🖨️ Automated Document Generation
* **PDF Invoicing:** Programmatically constructs and downloads professional, print-ready PDF receipts using `FPDF`.
* **Dynamic UPI QR Codes:** Auto-generates scannable payment QR codes embedded directly into the invoice using the `qrcode` library, pre-filled with the exact transaction total.

### 📦 Inventory & Operations Management
* **Automated Stock Deduction:** Syncs transactions with inventory tracking, preventing checkout if stock is insufficient.
* **Shift Tracking:** Logs cashier start/end times and tracks specific sales performance per shift.
* **Financial Reporting:** Dedicated expense tracking and aggregate sales reporting for business analytics.

---

## 💻 Tech Stack

**Backend:**
* Python 3.x
* Flask (Web Framework)
* Flask-SQLAlchemy (ORM for SQLite database management)
* Bcrypt (Security)
* PyFPDF & qrcode (Document generation)
* Pandas (Data handling/reporting)

**Frontend:**
* HTML5 / CSS3 (Responsive Grid Architecture)
* Vanilla JavaScript (DOM manipulation & async fetch calls)
* Jinja2 (Server-side template rendering)
* FontAwesome (Icons)

---

## 🗄️ Database Architecture

The application is built on a robust relational SQLite database with the following core models:
* `Login`: Manages user credentials, RBAC roles, and approval statuses.
* `Grocery`: Tracks product names, pricing, and live stock quantities.
* `Transaction`: Records historical sales, payment methods, applied discounts, and delivery metadata.
* `DeliveryLocation`: Maps serviceable PIN codes to specific delivery fees.
* `Coupons`: Stores discount codes, types, and strict usage limits.
* `Shifts` & `StockReport`: Maintains audit trails for employee hours and inventory lifecycle.

---

## 📸 Screenshots

*(Add your screenshots here by dragging and dropping images into your GitHub editor!)*
* **Admin Dashboard & Analytics**
* **POS Checkout Interface**
* **Generated PDF Invoice**

---

## ⚙️ Local Installation & Setup
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/retail-wizard.git](https://github.com/YOUR_USERNAME/retail-wizard.git)
   cd retail-wizard
  ```
2. **Set up a virtual environment (Recommended):**
```Bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activat
```
3. **Install dependencies:**
```Bash
pip install -r requirements.txt
```
4. **Initialize the application:**

```Bash
python run.py
```
*Note:* The SQLite database (app.db) will automatically generate upon the first run.

5. **First-Time Setup:**
Open your browser and navigate to http://127.0.0.1:5000. Register your first user account. The system is designed to automatically grant Admin privileges and bypass the approval queue for the very first registered user.

---

## 🌍 Multi-Device Testing via Ngrok (Optional)

Because Retail Wizard features a strict Role-Based Access Control (RBAC) system, the best way to test the application is across multiple devices (e.g., acting as the Admin on your PC and a Cashier on your smartphone). 

You can easily expose the local Flask server to the internet using [Ngrok](https://ngrok.com/):

1. **Start your local Flask application:**
```bash
python run.py
```
2. **In a separate terminal window, start Ngrok on port 5000:**
```Bash
ngrok http 5000
```
3. **Copy the Forwarding URL provided by Ngrok (e.g., https://random-string.ngrok-free.app).**
4. **Open that URL on your smartphone.**

5. **The Scenario Test:** Create a new account on your phone. Then, watch the pending request appear instantly on your PC's Admin Dashboard to approve or reject the new cashier in real-time!

## 👨‍💻 Author
Someshwar B.Tech Computer Science and Engineering Indian Institute of Information Technology, Vadodara (IIITV)
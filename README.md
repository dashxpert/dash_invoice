# 📄 Dashxpert - Freelancer Invoice & GST Management

Dashxpert is a Django-based SaaS platform designed for Indian freelancers, creators, and consultants. It helps manage clients, generate invoices, track revenue, and handle GST – all from one dashboard.

## 🚀 Features

- 👤 User authentication (Register/Login)
- 🧾 Invoice creation with branding
- 💸 GST-compliant billing
- 🏦 Bank & UPI details management
- 💳 Razorpay integration for plan upgrades
- 📊 Analytics dashboard (Pro plan only)
- 📬 Email invoices to clients
- 🖼️ Custom logo support (Pro plan)
- 🆓 Free & Starter plan limits enforced

## 📦 Pricing Plans

| Plan     | Price     | Features                                  |
|----------|-----------|-------------------------------------------|
| Free     | ₹0/mo     | 3 invoices/month, watermark, limited support |
| Starter  | ₹199/mo   | Unlimited invoices, PDF & GST reports      |
| Pro      | ₹499/mo   | All Starter features + Logo + Dashboard   |

## 🛠️ Tech Stack

- Python 3.12
- Django 5.x
- MySQL
- Razorpay API
- Bootstrap 5
- HTML/CSS

## 🧑‍💻 Local Setup

```bash
git clone https://github.com/dashxpert/dash_invoice.git
cd dash_invoice
python -m venv env
env\Scripts\activate  # On Windows
pip install -r requirements.txt

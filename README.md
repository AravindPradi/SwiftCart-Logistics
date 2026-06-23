# SwiftCart Logistics 🚚📦

A warehouse/product ordering and delivery management system built with pure **Django**, **SQLite**, and **Tailwind CSS**. It supports Role-Based Access Control (RBAC) with dedicated portals for Administrators, Customers, and Rider partners.

## Features

### 👤 Role-Based Portals & Authentication
- **Customer Portal:** Browse the product catalog with category filters/searches, manage a persistent shopping cart, save multiple delivery addresses, and track real-time transit timelines of orders.
- **Rider Portal:** Toggle online/offline status, view available unassigned deliveries, accept or reject delivery tasks, and step-by-step progress tracking (Rider Assigned ➔ Reached Warehouse ➔ Picked Up ➔ On The Way ➔ Delivered / Failed).
- **Admin Panel:** Complete inventory management (CRUD), low-stock warning banners, manual rider assignment, user profiles lists, and rider performance metrics (completed/failed deliveries ratio).

### ⚙️ Business Rules Implemented
- **One-accept assignment:** First rider to accept locks the order.
- **Rider rejections:** Riders will not see a delivery offer again once rejected.
- **Delivery restrictions:** Customers can only update their destination address *before* the rider picks up the shipment from the warehouse (i.e. status is less than `Picked Up`).
- **Inventory integrity:** Successful order placement reduces catalog stock. If stock is unavailable, checkout is blocked.

---

## Getting Started

### 📋 Prerequisites
- **Python 3.10+** (Python 3.13.1 was used during development)
- **Django 5.0+**

### 🚀 Running Locally

1. **Clone or navigate** to the project directory:

2. **Initialize migrations and database**:
   ```bash
   python manage.py makemigrations accounts products orders riders dashboard
   python manage.py migrate
   ```

3. **Populate the database with pre-configured seed data**:
   This runs a custom command to automatically set up standard Admin, Customer, and Rider users, categories, products, addresses, and sample active/completed orders:
   ```bash
   python manage.py seed_data
   ```

4. **Start the Django development server**:
   ```bash
   python manage.py runserver
   ```
   Open your browser and visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## 🔑 Demo Accounts (Seeded Data)

| Username | Password | Role / Account Type |
| :--- | :--- | :--- |
| `admin` | `adminpassword123` | **Admin/Warehouse Manager** |
| `john_doe` | `customerpass123` | **Customer** |
| `jane_smith` | `customerpass123` | **Customer** |
| `rider_mike` | `riderpass123` | **Rider (Online by default)** |
| `rider_sarah` | `riderpass123` | **Rider (Offline by default)** |

---

## 🛠️ Codebase Structure

```text
swiftcart_logistics/   # Project Settings & Root Router
accounts/              # Custom User & Rider/Customer Profiles
products/              # Warehouse Categories & Stock Levels
orders/                # Cart Items, Addresses, Orders & Timelines
riders/                # Rider Availability & Order Rejection Records
dashboard/             # Portals & Admin Management Panels
templates/             # Project-wide UI templates
static/                # Stylesheets & CSS assets
```
"# SwiftCart-Logistics" 

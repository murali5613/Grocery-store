# Grocery Store Management System

A full-stack web application for managing grocery store operations, including customer-facing features and inventory management.

## Features
- **User Authentication**: Registration, login, and session management
- **Product Management**:
  - Add/Edit/Delete products with images
  - Categorization system
  - Stock management
- **Shopping Cart**:
  - Add/Remove items
  - Quantity adjustment
  - Checkout system
- **Search & Filter**: Advanced product search across multiple fields
- **Admin Panel**:
  - Category management
  - Product inventory control
  - Manager authentication

## Installation
1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r req.txt
   ```
4. Initialize database:
   ```bash
   flask shell
   >>> from app import db
   >>> db.create_all()
   >>> exit()
   ```
5. Create required directories:
   ```bash
   mkdir -p static/img
   ```

## Usage
1. Start the development server:
   ```bash
   python app.py
   ```
2. Access in browser: `http://localhost:5000`

**User Roles:**
- **Customers**: Browse products, manage cart, checkout
- **Managers**: 
  - Access `/manager` for admin login
  - Manage categories at `/category`
  - Manage products at `/products`

## Project Structure
grocery-store/
├── app.py # Main application entry point
├── req.txt # Dependency requirements
├── static/
│ ├── css/ # CSS stylesheets
│ ├── js/ # JavaScript files
│ └── img/ # Product images storage
├── templates/ # Jinja2 HTML templates
│ ├── auth/ # Authentication templates
│ │ ├── login.html
│ │ └── register.html
│ ├── admin/ # Manager templates
│ │ ├── category.html
│ │ └── products.html
│ ├── cart.html # Shopping cart
│ ├── home.html # Main store page
│ └── base.html # Base template
└── venv/ # Virtual environment (ignored)

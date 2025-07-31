#!/usr/bin/env python3
"""
Vulnerable Flask Application - Basic SQL Injection
This is intentionally vulnerable for educational/testing purposes.
"""

from flask import Flask, request, render_template_string, redirect, url_for, session, flash
import sqlite3
import os
import random
import string

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

# Initialize database
def init_db():
    conn = sqlite3.connect('vuln_app.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL,
            description TEXT
        )
    ''')
    
    # Insert sample data
    cursor.execute("INSERT OR IGNORE INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                  ('admin', 'admin123', 'admin@vulnapp.com', 'admin'))
    cursor.execute("INSERT OR IGNORE INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                  ('user', 'password123', 'user@vulnapp.com', 'user'))
    cursor.execute("INSERT OR IGNORE INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                  ('test', 'test123', 'test@vulnapp.com', 'user'))
    
    cursor.execute("INSERT OR IGNORE INTO products (name, price, description) VALUES (?, ?, ?)",
                  ('Laptop', 999.99, 'High-performance laptop'))
    cursor.execute("INSERT OR IGNORE INTO products (name, price, description) VALUES (?, ?, ?)",
                  ('Phone', 599.99, 'Smartphone with camera'))
    
    conn.commit()
    conn.close()

# VULNERABLE: SQL Injection in login
def check_login(username, password):
    conn = sqlite3.connect('vuln_app.db')
    cursor = conn.cursor()
    
    # VULNERABLE: Direct string concatenation - SQL Injection possible
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    
    try:
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        return user
    except Exception as e:
        conn.close()
        return None

# VULNERABLE: SQL Injection in search
def search_products(search_term):
    conn = sqlite3.connect('vuln_app.db')
    cursor = conn.cursor()
    
    # VULNERABLE: Direct string concatenation - SQL Injection possible
    query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%' OR description LIKE '%{search_term}%'"
    
    try:
        cursor.execute(query)
        products = cursor.fetchall()
        conn.close()
        return products
    except Exception as e:
        conn.close()
        return []

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>VulnApp - Login</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 400px; margin: 0 auto; }
                input, button { width: 100%; padding: 10px; margin: 5px 0; }
                .error { color: red; }
                .success { color: green; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>VulnApp Login</h1>
                {% if error %}
                    <p class="error">{{ error }}</p>
                {% endif %}
                {% if success %}
                    <p class="success">{{ success }}</p>
                {% endif %}
                <form method="POST" action="/login">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit">Login</button>
                </form>
                <p><a href="/register">Register</a> | <a href="/search">Search Products</a></p>
            </div>
        </body>
        </html>
    ''', error=request.args.get('error'), success=request.args.get('success'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    if not username or not password:
        return redirect(url_for('index', error='Please provide username and password'))
    
    user = check_login(username, password)
    
    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['role'] = user[4]
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('index', error='Invalid credentials'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard - VulnApp</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { display: flex; justify-content: space-between; align-items: center; }
                .admin-panel { background: #ffebee; padding: 20px; margin: 20px 0; border: 1px solid #f44336; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome, {{ session.username }}!</h1>
                    <a href="/logout">Logout</a>
                </div>
                
                <p>Role: {{ session.role }}</p>
                
                {% if session.role == 'admin' %}
                <div class="admin-panel">
                    <h2>Admin Panel</h2>
                    <p>Congratulations! You have access to the admin panel.</p>
                    <p>This is where sensitive operations would be performed.</p>
                    <ul>
                        <li>User Management</li>
                        <li>System Configuration</li>
                        <li>Database Administration</li>
                    </ul>
                </div>
                {% endif %}
                
                <h2>User Dashboard</h2>
                <p>This is your personal dashboard. You can:</p>
                <ul>
                    <li><a href="/search">Search Products</a></li>
                    <li><a href="/profile">View Profile</a></li>
                </ul>
            </div>
        </body>
        </html>
    ''')

@app.route('/search')
def search_page():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Search Products - VulnApp</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                input, button { padding: 10px; margin: 5px; }
                .product { border: 1px solid #ddd; padding: 10px; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Search Products</h1>
                <form method="GET" action="/search">
                    <input type="text" name="q" placeholder="Search products..." value="{{ request.args.get('q', '') }}">
                    <button type="submit">Search</button>
                </form>
                
                {% if products %}
                <h2>Search Results:</h2>
                {% for product in products %}
                <div class="product">
                    <h3>{{ product[1] }}</h3>
                    <p>Price: ${{ product[2] }}</p>
                    <p>{{ product[3] }}</p>
                </div>
                {% endfor %}
                {% endif %}
                
                <p><a href="/">Back to Home</a></p>
            </div>
        </body>
        </html>
    ''', products=search_products(request.args.get('q', '')) if request.args.get('q') else [])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index', success='Logged out successfully'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=True) 
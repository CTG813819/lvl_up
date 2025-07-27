#!/usr/bin/env python3
"""
Vulnerable Flask Application - Reflected XSS
This is intentionally vulnerable for educational/testing purposes.
"""

from flask import Flask, request, render_template_string, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import random
import string
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

# Initialize database
def init_db():
    conn = sqlite3.connect('xss_app.db')
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
    
    # Create comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users (id)
        )
    ''')
    
    # Insert sample data
    cursor.execute("INSERT OR IGNORE INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                  ('admin', 'xss_admin_2024', 'admin@xssapp.com', 'admin'))
    cursor.execute("INSERT OR IGNORE INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                  ('user', 'xss_user_2024', 'user@xssapp.com', 'user'))
    cursor.execute("INSERT OR IGNORE INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                  ('guest', 'guest123', 'guest@xssapp.com', 'guest'))
    
    cursor.execute("INSERT OR IGNORE INTO posts (title, content, author_id) VALUES (?, ?, ?)",
                  ('Welcome to XSSApp', 'This is a vulnerable web application for testing XSS attacks.', 1))
    cursor.execute("INSERT OR IGNORE INTO posts (title, content, author_id) VALUES (?, ?, ?)",
                  ('Security Notice', 'This app is intentionally vulnerable. Do not use in production.', 1))
    
    conn.commit()
    conn.close()

# VULNERABLE: Weak XSS filter
def filter_xss(text):
    """Weak XSS filter that can be bypassed."""
    # Very basic filter - easily bypassed
    filtered = text.replace('<script>', '').replace('</script>', '')
    filtered = filtered.replace('javascript:', '')
    return filtered

# VULNERABLE: No proper escaping in search
def search_posts(search_term):
    conn = sqlite3.connect('xss_app.db')
    cursor = conn.cursor()
    
    # VULNERABLE: Direct string concatenation with weak filtering
    filtered_term = filter_xss(search_term)
    query = f"SELECT * FROM posts WHERE title LIKE '%{filtered_term}%' OR content LIKE '%{filtered_term}%'"
    
    try:
        cursor.execute(query)
        posts = cursor.fetchall()
        conn.close()
        return posts, filtered_term  # Return both results and the filtered term
    except Exception as e:
        conn.close()
        return [], filtered_term

# VULNERABLE: Stored XSS in comments
def add_comment(user_id, content):
    conn = sqlite3.connect('xss_app.db')
    cursor = conn.cursor()
    
    # VULNERABLE: Weak filtering before storage
    filtered_content = filter_xss(content)
    
    cursor.execute("INSERT INTO comments (user_id, content) VALUES (?, ?)", (user_id, filtered_content))
    conn.commit()
    conn.close()

def get_comments():
    conn = sqlite3.connect('xss_app.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.content, u.username, c.created_at 
        FROM comments c 
        JOIN users u ON c.user_id = u.id 
        ORDER BY c.created_at DESC
    """)
    comments = cursor.fetchall()
    conn.close()
    return comments

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>XSSApp - Vulnerable Web Application</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
                .header { text-align: center; margin-bottom: 30px; }
                .nav { display: flex; justify-content: space-around; margin: 20px 0; }
                .nav a { padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }
                .nav a:hover { background: #0056b3; }
                .search-box { margin: 20px 0; }
                input, textarea, button { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
                .post { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; }
                .comment { background: #f9f9f9; padding: 10px; margin: 5px 0; border-left: 3px solid #007bff; }
                .error { color: red; }
                .success { color: green; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>XSSApp</h1>
                    <p>A vulnerable web application for testing XSS attacks</p>
                </div>
                
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/search">Search</a>
                    <a href="/posts">Posts</a>
                    <a href="/comments">Comments</a>
                    {% if session.user_id %}
                        <a href="/dashboard">Dashboard</a>
                        <a href="/logout">Logout</a>
                    {% else %}
                        <a href="/login">Login</a>
                    {% endif %}
                </div>
                
                <div class="search-box">
                    <form method="GET" action="/search">
                        <input type="text" name="q" placeholder="Search posts..." required>
                        <button type="submit">Search</button>
                    </form>
                </div>
                
                <h2>Recent Posts</h2>
                {% for post in posts %}
                <div class="post">
                    <h3>{{ post[1] }}</h3>
                    <p>{{ post[2] }}</p>
                    <small>Posted on {{ post[4] }}</small>
                </div>
                {% endfor %}
                
                {% if error %}
                    <p class="error">{{ error }}</p>
                {% endif %}
                {% if success %}
                    <p class="success">{{ success }}</p>
                {% endif %}
            </div>
        </body>
        </html>
    ''', posts=get_posts(), error=request.args.get('error'), success=request.args.get('success'))

@app.route('/search')
def search_page():
    search_term = request.args.get('q', '')
    posts, filtered_term = search_posts(search_term) if search_term else ([], '')
    
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Search - XSSApp</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
                .nav { display: flex; justify-content: space-around; margin: 20px 0; }
                .nav a { padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }
                input, button { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
                .post { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; }
                .search-results { margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/search">Search</a>
                    <a href="/posts">Posts</a>
                    <a href="/comments">Comments</a>
                    {% if session.user_id %}
                        <a href="/dashboard">Dashboard</a>
                        <a href="/logout">Logout</a>
                    {% else %}
                        <a href="/login">Login</a>
                    {% endif %}
                </div>
                
                <h1>Search Posts</h1>
                <form method="GET" action="/search">
                    <input type="text" name="q" placeholder="Search posts..." value="{{ search_term }}" required>
                    <button type="submit">Search</button>
                </form>
                
                {% if search_term %}
                <div class="search-results">
                    <h2>Search Results for: {{ filtered_term | safe }}</h2>
                    
                    {% if posts %}
                        {% for post in posts %}
                        <div class="post">
                            <h3>{{ post[1] | safe }}</h3>
                            <p>{{ post[2] | safe }}</p>
                            <small>Posted on {{ post[4] }}</small>
                        </div>
                        {% endfor %}
                    {% else %}
                        <p>No posts found matching your search.</p>
                    {% endif %}
                </div>
                {% endif %}
                
                <p><a href="/">Back to Home</a></p>
            </div>
        </body>
        </html>
    ''', search_term=search_term, filtered_term=filtered_term, posts=posts)

@app.route('/comments')
def comments_page():
    comments = get_comments()
    
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Comments - XSSApp</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
                .nav { display: flex; justify-content: space-around; margin: 20px 0; }
                .nav a { padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }
                input, textarea, button { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
                .comment { background: #f9f9f9; padding: 10px; margin: 5px 0; border-left: 3px solid #007bff; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/search">Search</a>
                    <a href="/posts">Posts</a>
                    <a href="/comments">Comments</a>
                    {% if session.user_id %}
                        <a href="/dashboard">Dashboard</a>
                        <a href="/logout">Logout</a>
                    {% else %}
                        <a href="/login">Login</a>
                    {% endif %}
                </div>
                
                <h1>Comments</h1>
                
                {% if session.user_id %}
                <form method="POST" action="/add_comment">
                    <textarea name="content" placeholder="Write a comment..." required></textarea>
                    <button type="submit">Add Comment</button>
                </form>
                {% else %}
                <p><a href="/login">Login to add comments</a></p>
                {% endif %}
                
                <h2>Recent Comments</h2>
                {% for comment in comments %}
                <div class="comment">
                    <p>{{ comment[0] | safe }}</p>
                    <small>By {{ comment[1] }} on {{ comment[2] }}</small>
                </div>
                {% endfor %}
                
                <p><a href="/">Back to Home</a></p>
            </div>
        </body>
        </html>
    ''', comments=comments)

@app.route('/add_comment', methods=['POST'])
def add_comment_route():
    if 'user_id' not in session:
        return redirect(url_for('comments_page'))
    
    content = request.form.get('content', '')
    if content:
        add_comment(session['user_id'], content)
    
    return redirect(url_for('comments_page'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Simple authentication (in real app, use proper hashing)
        if username == 'admin' and password == 'xss_admin_2024':
            session['user_id'] = 1
            session['username'] = 'admin'
            session['role'] = 'admin'
            return redirect(url_for('index', success='Logged in as admin'))
        elif username == 'user' and password == 'xss_user_2024':
            session['user_id'] = 2
            session['username'] = 'user'
            session['role'] = 'user'
            return redirect(url_for('index', success='Logged in as user'))
        else:
            return redirect(url_for('login', error='Invalid credentials'))
    
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login - XSSApp</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
                input, button { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
                .error { color: red; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Login</h1>
                {% if error %}
                    <p class="error">{{ error }}</p>
                {% endif %}
                <form method="POST">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit">Login</button>
                </form>
                <p><a href="/">Back to Home</a></p>
            </div>
        </body>
        </html>
    ''', error=request.args.get('error'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index', success='Logged out successfully'))

def get_posts():
    conn = sqlite3.connect('xss_app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY created_at DESC LIMIT 5")
    posts = cursor.fetchall()
    conn.close()
    return posts

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=True) 
import sqlite3
# Import Flask components:
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
# Import password hashing helpers:
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Config: Database path
DATABASE = 'taskmanager.db'

# Config: Cryptographic secret key for signing session cookies
app.secret_key = 'dev-secret-key-change-in-production'

def get_db():
    """
    Helper function to get/open a database connection.
    Stores the connection on Flask's request context global object 'g'.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exception):
    """
    Tears down database connections automatically when requests complete.
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ==========================================================================
# AUTHENTICATION ROUTES (From Milestones 1 - 3)
# ==========================================================================

@app.route('/')
def home():
    """Renders the landing homepage."""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles registering a new user with password hashing."""
    if request.method == 'POST':
        fullname = request.form.get('fullName', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirmPassword', '')

        if not fullname or not username or not email or not password:
            flash('All fields are required!', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')

        db = get_db()
        try:
            cursor = db.cursor()
            existing_user = cursor.execute(
                'SELECT id FROM users WHERE username = ? OR email = ?',
                (username, email)
            ).fetchone()

            if existing_user:
                flash('Username or Email already registered!', 'error')
                return render_template('register.html')

            hashed_password = generate_password_hash(password)

            cursor.execute(
                'INSERT INTO users (fullname, username, email, password) VALUES (?, ?, ?, ?)',
                (fullname, username, email, hashed_password)
            )
            db.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

        except sqlite3.Error as e:
            flash(f'An error occurred: {e}', 'error')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticates the user and initiates cookie sessions."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('login.html')

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['fullname'] = user['fullname']
            
            flash(f"Welcome back, {user['fullname']}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs out the user and clears sessions."""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))

# ==========================================================================
# TASK CRUD & CONTROL ROUTES (New / Updated in Milestone 5)
# ==========================================================================

@app.route('/dashboard')
def dashboard():
    """
    Renders user dashboard with:
    - Overall statistics counts (calculated efficiently in SQL)
    - Search input, status & priority dropdown selectors, and sorting orders
    - Dynamic list of filtered/sorted task cards
    """
    if 'user_id' not in session:
        flash('Please login to access the dashboard.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    db = get_db()

    # 1. Fetch search, filter, and sort GET query parameters from URL request args
    search = request.args.get('search', '').strip()
    status = request.args.get('status', 'All').strip()
    priority = request.args.get('priority', 'All').strip()
    sort = request.args.get('sort', 'due_date_desc').strip()

    # 2. Query overall statistics counts for this user (not affected by filters)
    # Using SQL aggregators (COUNT, SUM) avoids fetching rows into Python memory.
    stats = db.execute('''
        SELECT 
            COUNT(id) as total,
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN priority = 'High' THEN 1 ELSE 0 END) as high_priority
        FROM tasks 
        WHERE user_id = ?
    ''', (user_id,)).fetchone()

    # Extract stats variables, fallback to 0 if there are no tasks yet
    total_tasks = stats['total'] or 0
    pending_tasks = stats['pending'] or 0
    completed_tasks = stats['completed'] or 0
    high_priority_tasks = stats['high_priority'] or 0

    # 3. Build the dynamic task SELECT query
    query = 'SELECT * FROM tasks WHERE user_id = ?'
    params = [user_id]

    # Search condition: searches by title OR description
    if search:
        query += ' AND (title LIKE ? OR description LIKE ?)'
        params.append(f'%{search}%')
        params.append(f'%{search}%')

    # Status filter condition
    if status != 'All':
        query += ' AND status = ?'
        params.append(status)

    # Priority filter condition
    if priority != 'All':
        query += ' AND priority = ?'
        params.append(priority)

    # Sorting order conditions
    if sort == 'due_date_asc':
        # Due Date (Oldest First): Null or blank dates are pushed to the end (using CASE check)
        query += ' ORDER BY CASE WHEN due_date IS NULL OR due_date = "" THEN 1 ELSE 0 END, due_date ASC'
    elif sort == 'due_date_desc':
        # Due Date (Newest First): Null or blank dates are pushed to the end
        query += ' ORDER BY CASE WHEN due_date IS NULL OR due_date = "" THEN 1 ELSE 0 END, due_date DESC'
    elif sort == 'priority':
        # Sort by custom priority order: High -> Medium -> Low
        query += " ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 ELSE 4 END"
    else:
        # Default: newest task created first
        query += ' ORDER BY id DESC'

    # Execute the final dynamic query
    tasks = db.execute(query, params).fetchall()

    return render_template(
        'dashboard.html',
        tasks=tasks,
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        high_priority_tasks=high_priority_tasks,
        # Pass parameters back to templates to preserve control state highlights
        search=search,
        status=status,
        priority=priority,
        sort=sort
    )

@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    """Creates a new task record."""
    if 'user_id' not in session:
        flash('Please login to create a task.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'Medium')
        due_date = request.form.get('dueDate', '').strip()

        if not title:
            flash('Task title is required!', 'error')
            return render_template('add_task.html')

        db = get_db()
        try:
            db.execute(
                'INSERT INTO tasks (title, description, priority, due_date, status, user_id) VALUES (?, ?, ?, ?, ?, ?)',
                (title, description, priority, due_date, 'Pending', session['user_id'])
            )
            db.commit()
            # Success flash message
            flash('Task added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except sqlite3.Error as e:
            flash(f'Database error: {e}', 'error')
            return render_template('add_task.html')

    return render_template('add_task.html')

@app.route('/edit-task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    """Modifies an existing task record. Verifies owner authorization."""
    if 'user_id' not in session:
        flash('Please login to edit tasks.', 'error')
        return redirect(url_for('login'))

    db = get_db()
    task = db.execute('SELECT * FROM tasks WHERE id = ?', (id,)).fetchone()

    # Security Ownership Verification
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('dashboard'))
    
    if task['user_id'] != session['user_id']:
        flash('Access Denied: You cannot modify another user\'s tasks!', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'Medium')
        due_date = request.form.get('dueDate', '').strip()

        if not title:
            flash('Task title cannot be blank!', 'error')
            return render_template('edit_task.html', task=task)

        try:
            db.execute(
                'UPDATE tasks SET title = ?, description = ?, priority = ?, due_date = ? WHERE id = ?',
                (title, description, priority, due_date, id)
            )
            db.commit()
            # Success flash message
            flash('Task updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        except sqlite3.Error as e:
            flash(f'Database error: {e}', 'error')
            return render_template('edit_task.html', task=task)

    return render_template('edit_task.html', task=task)

@app.route('/delete-task/<int:id>')
def delete_task(id):
    """Deletes a task record. Verifies owner authorization."""
    if 'user_id' not in session:
        flash('Please login to delete tasks.', 'error')
        return redirect(url_for('login'))

    db = get_db()
    task = db.execute('SELECT * FROM tasks WHERE id = ?', (id,)).fetchone()

    # Security Ownership Verification
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('dashboard'))

    if task['user_id'] != session['user_id']:
        flash('Access Denied: You cannot delete another user\'s tasks!', 'error')
        return redirect(url_for('dashboard'))

    try:
        db.execute('DELETE FROM tasks WHERE id = ?', (id,))
        db.commit()
        # Success flash message
        flash('Task deleted successfully!', 'success')
    except sqlite3.Error as e:
        flash(f'Database error: {e}', 'error')

    return redirect(url_for('dashboard'))

@app.route('/complete-task/<int:id>')
def complete_task(id):
    """Marks task status as Completed. Verifies owner authorization."""
    if 'user_id' not in session:
        flash('Please login to complete tasks.', 'error')
        return redirect(url_for('login'))

    db = get_db()
    task = db.execute('SELECT * FROM tasks WHERE id = ?', (id,)).fetchone()

    # Security Ownership Verification
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('dashboard'))

    if task['user_id'] != session['user_id']:
        flash('Access Denied: You cannot complete another user\'s tasks!', 'error')
        return redirect(url_for('dashboard'))

    try:
        db.execute("UPDATE tasks SET status = 'Completed' WHERE id = ?", (id,))
        db.commit()
        # Success flash message
        flash('Task completed successfully!', 'success')
    except sqlite3.Error as e:
        flash(f'Database error: {e}', 'error')

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import sqlite3
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'carissa_school_secret_key_2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'mp4', 'avi', 'mov'}

DATABASE = 'database/school.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT,
                role TEXT NOT NULL,
                grade TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # News and events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                image_path TEXT,
                author_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users (id)
            )
        ''')
        
        # Gallery table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gallery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                image_path TEXT NOT NULL,
                uploaded_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (uploaded_by) REFERENCES users (id)
            )
        ''')
        
        # Admissions info table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                fees_structure TEXT,
                requirements TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Educational activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                grade TEXT NOT NULL,
                subject TEXT,
                content_type TEXT,
                file_path TEXT,
                video_url TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # Custom pages table for code editor
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_name TEXT UNIQUE NOT NULL,
                html_content TEXT,
                css_content TEXT,
                js_content TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create default admin user if not exists
        cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
        if not cursor.fetchone():
            hashed_password = generate_password_hash('admin123')
            cursor.execute('''
                INSERT INTO users (username, password, full_name, email, role)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', hashed_password, 'Administrator', 'carissaschool@telkomsa.net', 'admin'))
        
        # Create default admissions content
        cursor.execute('SELECT * FROM admissions')
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO admissions (content, fees_structure, requirements)
                VALUES (?, ?, ?)
            ''', (
                'Welcome to Carissa Primary School admissions. We accept applications throughout the year.',
                'Grade R: R15,000 per year\nGrade 1-3: R18,000 per year\nGrade 4-7: R20,000 per year',
                'Birth certificate\nProof of residence\nImmunization records\nPrevious school reports (if applicable)'
            ))
        
        db.commit()
        db.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') not in ['admin', 'teacher']:
            flash('Teacher or Admin access required', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Public routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/digest')
def digest():
    db = get_db()
    news_items = db.execute('SELECT * FROM news ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('digest.html', news_items=news_items)

@app.route('/gallery')
def gallery():
    db = get_db()
    images = db.execute('SELECT * FROM gallery ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('gallery.html', images=images)

@app.route('/admissions')
def admissions():
    db = get_db()
    admission_info = db.execute('SELECT * FROM admissions ORDER BY id DESC LIMIT 1').fetchone()
    db.close()
    return render_template('admissions.html', info=admission_info)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/elearning')
def elearning():
    return render_template('elearning.html')

@app.route('/admin/elearning-config')
@admin_required
def admin_elearning_config():
    return render_template('admin_elearning_config.html')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        db.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['role'] = user['role']
            session['grade'] = user['grade'] if user['grade'] else None
            
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Student dashboard
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('index'))
    
    grade = session.get('grade')
    db = get_db()
    activities = db.execute('''
        SELECT * FROM activities 
        WHERE grade = ? OR grade = 'All Grades'
        ORDER BY created_at DESC
    ''', (grade,)).fetchall()
    db.close()
    
    return render_template('student_dashboard.html', activities=activities)

# Teacher dashboard
@app.route('/teacher/dashboard')
@teacher_or_admin_required
def teacher_dashboard():
    db = get_db()
    activities = db.execute('''
        SELECT * FROM activities 
        WHERE created_by = ?
        ORDER BY created_at DESC
    ''', (session['user_id'],)).fetchall()
    db.close()
    
    return render_template('teacher_dashboard.html', activities=activities)

@app.route('/teacher/add-activity', methods=['GET', 'POST'])
@teacher_or_admin_required
def add_activity():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        grade = request.form['grade']
        subject = request.form['subject']
        content_type = request.form['content_type']
        video_url = request.form.get('video_url', '')
        
        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'activities', filename)
                file.save(filepath)
                file_path = f"uploads/activities/{filename}"
        
        db = get_db()
        db.execute('''
            INSERT INTO activities (title, description, grade, subject, content_type, file_path, video_url, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, grade, subject, content_type, file_path, video_url, session['user_id']))
        db.commit()
        db.close()
        
        flash('Activity added successfully!', 'success')
        return redirect(url_for('teacher_dashboard'))
    
    return render_template('add_activity.html')

# Admin dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    db = get_db()
    stats = {
        'total_users': db.execute('SELECT COUNT(*) as count FROM users').fetchone()['count'],
        'total_students': db.execute('SELECT COUNT(*) as count FROM users WHERE role = "student"').fetchone()['count'],
        'total_teachers': db.execute('SELECT COUNT(*) as count FROM users WHERE role = "teacher"').fetchone()['count'],
        'total_news': db.execute('SELECT COUNT(*) as count FROM news').fetchone()['count'],
        'total_activities': db.execute('SELECT COUNT(*) as count FROM activities').fetchone()['count']
    }
    db.close()
    return render_template('admin_dashboard.html', stats=stats)

@app.route('/admin/users')
@admin_required
def admin_users():
    db = get_db()
    users = db.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('admin_users.html', users=users)

@app.route('/admin/add-user', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        email = request.form['email']
        role = request.form['role']
        grade = request.form.get('grade', None)
        
        hashed_password = generate_password_hash(password)
        
        try:
            db = get_db()
            db.execute('''
                INSERT INTO users (username, password, full_name, email, role, grade)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, full_name, email, role, grade))
            db.commit()
            db.close()
            flash(f'User {username} created successfully!', 'success')
            return redirect(url_for('admin_users'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'danger')
    
    return render_template('add_user.html')

@app.route('/admin/manage-news')
@admin_required
def manage_news():
    db = get_db()
    news_items = db.execute('SELECT * FROM news ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('manage_news.html', news_items=news_items)

@app.route('/admin/add-news', methods=['GET', 'POST'])
@admin_required
def add_news():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'news', filename)
                file.save(filepath)
                image_path = f"uploads/news/{filename}"
        
        db = get_db()
        db.execute('''
            INSERT INTO news (title, content, category, image_path, author_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, category, image_path, session['user_id']))
        db.commit()
        db.close()
        
        flash('News item added successfully!', 'success')
        return redirect(url_for('manage_news'))
    
    return render_template('add_news.html')

@app.route('/admin/edit-news/<int:news_id>', methods=['GET', 'POST'])
@admin_required
def edit_news(news_id):
    db = get_db()
    news_item = db.execute('SELECT * FROM news WHERE id = ?', (news_id,)).fetchone()
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        
        image_path = news_item['image_path']
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'news', filename)
                file.save(filepath)
                image_path = f"uploads/news/{filename}"
        
        db.execute('''
            UPDATE news 
            SET title = ?, content = ?, category = ?, image_path = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title, content, category, image_path, news_id))
        db.commit()
        db.close()
        
        flash('News updated successfully!', 'success')
        return redirect(url_for('manage_news'))
    
    db.close()
    return render_template('edit_news.html', news=news_item)

@app.route('/admin/delete-news/<int:news_id>')
@admin_required
def delete_news(news_id):
    db = get_db()
    db.execute('DELETE FROM news WHERE id = ?', (news_id,))
    db.commit()
    db.close()
    flash('News deleted successfully!', 'success')
    return redirect(url_for('manage_news'))

@app.route('/admin/manage-gallery')
@admin_required
def manage_gallery():
    db = get_db()
    images = db.execute('SELECT * FROM gallery ORDER BY created_at DESC').fetchall()
    db.close()
    return render_template('manage_gallery.html', images=images)

@app.route('/admin/add-gallery', methods=['GET', 'POST'])
@admin_required
def add_gallery():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'gallery', filename)
                file.save(filepath)
                image_path = f"uploads/gallery/{filename}"
                
                db = get_db()
                db.execute('''
                    INSERT INTO gallery (title, description, image_path, uploaded_by)
                    VALUES (?, ?, ?, ?)
                ''', (title, description, image_path, session['user_id']))
                db.commit()
                db.close()
                
                flash('Image added to gallery!', 'success')
                return redirect(url_for('manage_gallery'))
        
        flash('Please select an image file', 'danger')
    
    return render_template('add_gallery.html')

@app.route('/admin/delete-gallery/<int:image_id>')
@admin_required
def delete_gallery(image_id):
    db = get_db()
    db.execute('DELETE FROM gallery WHERE id = ?', (image_id,))
    db.commit()
    db.close()
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('manage_gallery'))

@app.route('/admin/edit-admissions', methods=['GET', 'POST'])
@admin_required
def edit_admissions():
    db = get_db()
    admission_info = db.execute('SELECT * FROM admissions ORDER BY id DESC LIMIT 1').fetchone()
    
    if request.method == 'POST':
        content = request.form['content']
        fees_structure = request.form['fees_structure']
        requirements = request.form['requirements']
        
        if admission_info:
            db.execute('''
                UPDATE admissions 
                SET content = ?, fees_structure = ?, requirements = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (content, fees_structure, requirements, admission_info['id']))
        else:
            db.execute('''
                INSERT INTO admissions (content, fees_structure, requirements)
                VALUES (?, ?, ?)
            ''', (content, fees_structure, requirements))
        
        db.commit()
        db.close()
        flash('Admissions information updated!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    db.close()
    return render_template('edit_admissions.html', info=admission_info)

@app.route('/admin/code-editor', methods=['GET', 'POST'])
@admin_required
def code_editor():
    db = get_db()
    
    if request.method == 'POST':
        page_name = request.form['page_name']
        html_content = request.form.get('html_content', '')
        css_content = request.form.get('css_content', '')
        js_content = request.form.get('js_content', '')
        
        existing = db.execute('SELECT * FROM custom_pages WHERE page_name = ?', (page_name,)).fetchone()
        
        if existing:
            db.execute('''
                UPDATE custom_pages 
                SET html_content = ?, css_content = ?, js_content = ?, updated_at = CURRENT_TIMESTAMP
                WHERE page_name = ?
            ''', (html_content, css_content, js_content, page_name))
        else:
            db.execute('''
                INSERT INTO custom_pages (page_name, html_content, css_content, js_content)
                VALUES (?, ?, ?, ?)
            ''', (page_name, html_content, css_content, js_content))
        
        db.commit()
        flash(f'Page "{page_name}" saved successfully!', 'success')
    
    pages = db.execute('SELECT * FROM custom_pages ORDER BY page_name').fetchall()
    db.close()
    
    return render_template('code_editor.html', pages=pages)

@app.route('/admin/load-page/<page_name>')
@admin_required
def load_page(page_name):
    db = get_db()
    page = db.execute('SELECT * FROM custom_pages WHERE page_name = ?', (page_name,)).fetchone()
    db.close()
    
    if page:
        return jsonify({
            'html': page['html_content'],
            'css': page['css_content'],
            'js': page['js_content']
        })
    return jsonify({'error': 'Page not found'}), 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

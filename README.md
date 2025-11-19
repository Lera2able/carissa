# Carissa Primary School Website

A comprehensive school management website with admin panel, content management system, and educational platform for students.

## Features

### Public Pages
- **Homepage**: About the school with statistics and quick links
- **School Digest**: News, events, and newsletters
- **Picture Gallery**: Photo gallery from school events
- **Admissions**: Enrollment information and fees structure
- **Contact**: Contact form and school information

### User Roles

#### Admin
- Full access to all features
- User management (create students, teachers, admins)
- Content management (news, gallery, admissions)
- Code editor for custom page creation
- System statistics dashboard

#### Teacher
- Add and manage educational activities
- Upload learning resources and videos
- Create content for specific grade levels

#### Student
- Access grade-specific educational content
- View learning activities and games
- Download resources and watch educational videos

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt --break-system-packages
```

### 2. Run the Application
```bash
python app.py
```

The website will be available at: http://localhost:5000

### 3. Default Login Credentials
- **Username**: admin
- **Password**: admin123

**Important**: Change these credentials after first login!

## Directory Structure
```
carissa_school_website/
├── app.py                 # Main Flask application
├── database/             # SQLite database
│   └── school.db
├── static/
│   ├── css/
│   │   └── style.css    # Main stylesheet
│   ├── images/
│   │   └── logo.jpg     # School logo
│   └── uploads/         # User uploaded content
│       ├── news/
│       ├── gallery/
│       └── activities/
└── templates/           # HTML templates
    ├── base.html
    ├── index.html
    ├── digest.html
    ├── gallery.html
    ├── admissions.html
    ├── contact.html
    ├── login.html
    ├── admin_dashboard.html
    ├── teacher_dashboard.html
    ├── student_dashboard.html
    └── ... (other templates)
```

## Usage Guide

### For Administrators

1. **Adding Users**
   - Go to Admin Dashboard → User Management
   - Click "Add User"
   - Fill in user details and select role
   - For students, specify their grade level

2. **Managing News**
   - Go to Admin Dashboard → School Digest
   - Add news items with images
   - Edit or delete existing news

3. **Gallery Management**
   - Upload photos to the picture gallery
   - Add titles and descriptions
   - Delete unwanted images

4. **Admissions Information**
   - Update enrollment details
   - Edit fees structure
   - Modify admission requirements

5. **Code Editor**
   - Create custom pages with HTML/CSS/JS
   - Save multiple page versions
   - Advanced customization options

### For Teachers

1. **Adding Activities**
   - Go to Dashboard → Add Activity
   - Select grade level and subject
   - Upload files or add video URLs
   - Students will see grade-specific content

### For Students

1. **Accessing Learning Resources**
   - Login with credentials provided by admin/teacher
   - View activities for your grade level
   - Download worksheets and watch videos

## Technical Details

- **Framework**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Session-based with password hashing
- **File Upload**: Supports images, PDFs, documents, videos

## Security Features

- Password hashing with Werkzeug
- Role-based access control
- Session management
- Secure file uploads with validation

## Database Tables

1. **users**: User accounts (students, teachers, admins)
2. **news**: School news and events
3. **gallery**: Photo gallery
4. **admissions**: Admission information
5. **activities**: Educational content
6. **custom_pages**: Custom HTML pages

## Customization

### Changing Colors
Edit `/static/css/style.css` and modify the CSS variables:
```css
:root {
    --primary-color: #00ACC1;
    --secondary-color: #0097A7;
    /* ... other colors */
}
```

### Adding New Pages
Use the Code Editor in the admin panel to create custom pages with HTML, CSS, and JavaScript.

## Deployment

### For Production Deployment:

1. Change the secret key in `app.py`
2. Use a production WSGI server (e.g., Gunicorn)
3. Set up proper file permissions
4. Configure SSL/HTTPS
5. Use environment variables for sensitive data
6. Regular database backups

### Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Support

For issues or questions, contact:
- Email: carissaschool@telkomsa.net
- Phone: 013 656 1286

## License

© 2024 Carissa Primary School. All rights reserved.

# 🏗️ Lab Management Dashboard

A Django-based Cluster Dashboard for efficiently managing clusters and nodes inventory in enterprise environments.


## 🛠️ Technology Stack

- **Backend**: Django 4.2+ (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: SQLite (development), MySQL/PostgreSQL ready
- **Data Processing**: Pandas for Excel import

## 📋 Project Structure

```
lab_management/
├── lab_management/          # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── dashboard/              # Main application
│   ├── __init__.py
│   ├── admin.py           # Django admin configuration
│   ├── apps.py
│   ├── models.py          # Database models
│   ├── urls.py            # App URL routing
│   ├── utils.py           # Utility functions
│   ├── views.py           # Business logic
│   └── templates/
│       └── dashboard/     # HTML templates
│           ├── base.html
│           ├── dashboard.html
│           ├── cluster_*.html
│           ├── node_*.html
│           └── import_excel.html
├── static/                # CSS, JS, images
├── media/                 # User uploads
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lab_management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

7. **Access the application**
   - Main application: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

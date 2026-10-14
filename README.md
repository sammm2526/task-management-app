# 📋 TaskFlow - Task Management Application

A full-stack Task Management web application built using **Flask, SQLite, HTML, CSS, and JavaScript**. The application helps users efficiently organize their daily tasks with secure authentication, task management features, and a responsive user interface.

---

## 🚀 Features

### 👤 User Authentication
- User Registration
- Secure Login & Logout
- Password Hashing using Werkzeug
- Session Management
- Protected Dashboard

### ✅ Task Management
- Create New Tasks
- View All Tasks
- Edit Existing Tasks
- Delete Tasks
- Mark Tasks as Completed

### 🔍 Advanced Features
- Search Tasks
- Filter Tasks by Status & Priority
- Sort Tasks by Due Date or Priority
- Dashboard Statistics
- Flash Success Messages
- Delete Confirmation Dialog
- Responsive Design

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask

### Database
- SQLite

### Authentication
- Flask Sessions
- Werkzeug Password Hashing

### Version Control
- Git
- GitHub

---

## 📂 Project Structure

```
task-management-app/
│
├── app.py
├── init_db.py
├── requirements.txt
├── taskmanager.db
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_task.html
│   └── edit_task.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/sammm2526/task-management-app.git
```

### 2. Navigate to the project

```bash
cd task-management-app
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the database

```bash
python init_db.py
```

### 5. Run the application

```bash
python app.py
```

### 6. Open your browser

```
http://127.0.0.1:5000
```

---

## 📊 Application Workflow

1. Register a new account.
2. Login securely.
3. Access your personal dashboard.
4. Create and manage tasks.
5. Search, filter, and sort tasks.
6. Mark tasks as completed.
7. Logout securely.

---

## 🔒 Security Features

- Passwords are securely hashed before storage.
- User sessions are managed using Flask.
- Protected routes require authentication.
- Users can only access and manage their own tasks.

---

## 🌟 Future Enhancements

- Email Verification
- Password Reset
- Dark Mode
- Calendar View
- Task Categories
- File Attachments
- Notifications
- Team Collaboration
- Task Export (CSV/PDF)

---

## 👩‍💻 Author

**Samiksha K S**

GitHub: https://github.com/sammm2526

---

## 📄 License

This project was developed for learning purposes as part of a Full-Stack Web Development Internship.

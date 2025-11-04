from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationship to tasks
    tasks = db.relationship('Task', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key to link task to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Optional: Link task to a class
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=True)
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50))  # e.g., "PHYS 203"
    professor = db.Column(db.String(100))
    room = db.Column(db.String(50))
    color = db.Column(db.String(7), default='#3498db')  # Hex color for UI
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key to link class to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    links = db.relationship('ClassLink', backref='parent_class', lazy=True, cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='class', lazy=True)
    
    def __repr__(self):
        return f'<Class {self.name}>'

class ClassLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key to link to class
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    
    def __repr__(self):
        return f'<ClassLink {self.title}>'
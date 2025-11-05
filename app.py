from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, login_manager
from models import User, Task
from forms import RegistrationForm, LoginForm, TaskForm
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-later'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studysync.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    from datetime import datetime, timedelta
    
    # Get all tasks for current user
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    
    # Calculate stats
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.completed])
    
    # Tasks completed this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    completed_this_week = len([t for t in tasks if t.completed and t.created_at >= week_ago])
    
    # Upcoming deadlines (next 7 days)
    upcoming_deadline = datetime.utcnow() + timedelta(days=7)
    upcoming_tasks = [t for t in tasks if t.due_date and not t.completed and t.due_date <= upcoming_deadline and t.due_date >= datetime.utcnow()]
    
    # Overdue tasks
    overdue_tasks = [t for t in tasks if t.due_date and not t.completed and t.due_date < datetime.utcnow()]
    
    stats = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
        'completed_this_week': completed_this_week,
        'upcoming_count': len(upcoming_tasks),
        'overdue_count': len(overdue_tasks)
    }
    
    return render_template('dashboard.html', tasks=tasks, stats=stats, now=datetime.utcnow())

@app.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    form = TaskForm()
    
    # Populate class choices
    form.class_id.choices = [(0, '-- No Class --')] + [(c.id, c.name) for c in Class.query.filter_by(user_id=current_user.id).all()]
    
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            priority=form.priority.data,
            class_id=form.class_id.data if form.class_id.data != 0 else None,
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('task_form.html', form=form, title='New Task')

@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Make sure user owns this task
    if task.user_id != current_user.id:
        flash('You do not have permission to edit this task.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = TaskForm()
    
    # Populate class choices
    form.class_id.choices = [(0, '-- No Class --')] + [(c.id, c.name) for c in Class.query.filter_by(user_id=current_user.id).all()]
    
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.priority = form.priority.data
        task.class_id = form.class_id.data if form.class_id.data != 0 else None
        task.completed = form.completed.data
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # Pre-populate form with existing data
    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
        form.due_date.data = task.due_date
        form.priority.data = task.priority
        form.class_id.data = task.class_id if task.class_id else 0
        form.completed.data = task.completed
    
    return render_template('task_form.html', form=form, title='Edit Task', task=task)

@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Make sure user owns this task
    if task.user_id != current_user.id:
        flash('You do not have permission to delete this task.', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/task/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Make sure user owns this task
    if task.user_id != current_user.id:
        flash('You do not have permission to modify this task.', 'danger')
        return redirect(url_for('dashboard'))
    
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('dashboard'))


from models import User, Task, Class, ClassLink
from forms import RegistrationForm, LoginForm, TaskForm, ClassForm, ClassLinkForm

# Add these routes after your existing routes:

@app.route('/classes')
@login_required
def classes():
    user_classes = Class.query.filter_by(user_id=current_user.id).order_by(Class.name).all()
    return render_template('classes.html', classes=user_classes)

@app.route('/class/new', methods=['GET', 'POST'])
@login_required
def new_class():
    form = ClassForm()
    if form.validate_on_submit():
        new_class = Class(
            name=form.name.data,
            code=form.code.data,
            professor=form.professor.data,
            room=form.room.data,
            color=form.color.data,
            notes=form.notes.data,
            user_id=current_user.id
        )
        db.session.add(new_class)
        db.session.commit()
        flash('Class added successfully!', 'success')
        return redirect(url_for('classes'))
    
    return render_template('class_form.html', form=form, title='Add New Class')

@app.route('/class/<int:class_id>')
@login_required
def view_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    
    # Make sure user owns this class
    if class_obj.user_id != current_user.id:
        flash('You do not have permission to view this class.', 'danger')
        return redirect(url_for('classes'))
    
    # Get tasks related to this class
    class_tasks = Task.query.filter_by(class_id=class_id, user_id=current_user.id).all()
    
    return render_template('view_class.html', class_obj=class_obj, tasks=class_tasks)

@app.route('/class/<int:class_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    
    # Make sure user owns this class
    if class_obj.user_id != current_user.id:
        flash('You do not have permission to edit this class.', 'danger')
        return redirect(url_for('classes'))
    
    form = ClassForm()
    
    if form.validate_on_submit():
        class_obj.name = form.name.data
        class_obj.code = form.code.data
        class_obj.professor = form.professor.data
        class_obj.room = form.room.data
        class_obj.color = form.color.data
        class_obj.notes = form.notes.data
        db.session.commit()
        flash('Class updated successfully!', 'success')
        return redirect(url_for('view_class', class_id=class_id))
    
    # Pre-populate form
    elif request.method == 'GET':
        form.name.data = class_obj.name
        form.code.data = class_obj.code
        form.professor.data = class_obj.professor
        form.room.data = class_obj.room
        form.color.data = class_obj.color
        form.notes.data = class_obj.notes
    
    return render_template('class_form.html', form=form, title='Edit Class')

@app.route('/class/<int:class_id>/delete', methods=['POST'])
@login_required
def delete_class(class_id):
    class_obj = Class.query.get_or_404(class_id)
    
    # Make sure user owns this class
    if class_obj.user_id != current_user.id:
        flash('You do not have permission to delete this class.', 'danger')
        return redirect(url_for('classes'))
    
    db.session.delete(class_obj)
    db.session.commit()
    flash('Class deleted successfully!', 'success')
    return redirect(url_for('classes'))

@app.route('/class/<int:class_id>/link/new', methods=['GET', 'POST'])
@login_required
def add_link(class_id):
    class_obj = Class.query.get_or_404(class_id)
    
    # Make sure user owns this class
    if class_obj.user_id != current_user.id:
        flash('You do not have permission to add links to this class.', 'danger')
        return redirect(url_for('classes'))
    
    form = ClassLinkForm()
    if form.validate_on_submit():
        link = ClassLink(
            title=form.title.data,
            url=form.url.data,
            class_id=class_id
        )
        db.session.add(link)
        db.session.commit()
        flash('Link added successfully!', 'success')
        return redirect(url_for('view_class', class_id=class_id))
    
    return render_template('link_form.html', form=form, class_obj=class_obj)

@app.route('/link/<int:link_id>/delete', methods=['POST'])
@login_required
def delete_link(link_id):
    link = ClassLink.query.get_or_404(link_id)
    class_obj = Class.query.get_or_404(link.class_id)
    
    # Make sure user owns this class
    if class_obj.user_id != current_user.id:
        flash('You do not have permission to delete this link.', 'danger')
        return redirect(url_for('classes'))
    
    db.session.delete(link)
    db.session.commit()
    flash('Link deleted successfully!', 'success')
    return redirect(url_for('view_class', class_id=class_obj.id))

if __name__ == '__main__':
    app.run(debug=True)
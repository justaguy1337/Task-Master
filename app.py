from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime, timezone
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(os.getcwd(), 'test.db')
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Task %r' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        task_content = request.form['content'].strip()

        tasks = Todo.query.order_by(Todo.date_created).all()

        if not task_content:
            error = "Task content cannot be empty."
            return render_template('index.html', tasks=tasks, error=error)

        existing_task = Todo.query.filter(func.lower(
            Todo.content) == task_content.lower()).first()
        if existing_task:
            error = "Task already exists."
            return render_template('index.html', tasks=tasks, error=error)

        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue adding your task ¯\_(ツ)_/¯)"
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task ¯\_(ツ)_/¯'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == "POST":
        updated_content = request.form['content'].strip()

        if not updated_content:
            error = "Task content cannot be empty."
            return render_template('update.html', task=task, error=error)

        existing_task = Todo.query.filter(
            func.lower(Todo.content) == updated_content.lower(),
            Todo.id != id
        ).first()
        if existing_task:
            error = "Task with this content already exists."
            return render_template('update.html', task=task, error=error)

        task.content = updated_content

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task ¯\_(ツ)_/¯'
    else:
        return render_template('update.html', task=task)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables created!")
    app.run(debug=True)

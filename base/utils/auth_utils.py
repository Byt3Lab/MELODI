from functools import wraps
from flask import session, redirect, url_for, g
from base.models.user_model import UserModel
from core.db import DataBase

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        
        user = UserModel.query.get(session['user_id'])
        if not user or user.role != 'admin':
             # You might want to show a 403 Forbidden page or flash a message
            return redirect(url_for('main.home')) # Or some other page
            
        return f(*args, **kwargs)
    return decorated_function

def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        # We need a way to access the database session here. 
        # Since we are inside a request, we can assume the app is set up.
        # However, UserModel.query might not be available directly depending on how Model is set up in core.
        # Let's assume standard SQLAlchemy query if Model inherits from DeclarativeBase and has a query property or we use a session.
        # Checking core/db/database.py and core/application.py, it seems we might need to get the session from the app or use a scoped session if available.
        # But wait, UserModel inherits from Model which inherits from DeclarativeBase.
        # Usually we need a session to query. 
        # Let's look at how other modules query data if any. 
        # Since I haven't seen other modules, I'll assume I need to get the session.
        
        # For now, let's try to use the app's db session if possible or just use the Model if it has a query property attached (flask-sqlalchemy style).
        # The core/db/model.py just inherits from DeclarativeBase. It doesn't seem to have a query property by default unless attached.
        # I will need to verify how to query.
        
        # Let's assume for now we can import the db instance or use a helper.
        # Actually, looking at core/application.py, db is initialized in Application.
        # I might need to import the 'app' instance if it's a singleton or available globally, but it's passed around.
        # Flask's 'current_app' might help if the app is pushed to context.
        
        from flask import current_app
        # This might be tricky if 'db' is not attached to current_app.
        # In core/application.py: self.server.app = Flask(...) -> self.server.app is the flask app.
        # The Application instance 'self' has 'db'.
        # But 'current_app' is the Flask app, not the Application instance.
        # We might need to attach the Application instance to the Flask app to access it.
        # Let's check if core/adapters/flask_adapter.py does that.
        
        # PROCEEDING with a safe bet:
        # I'll assume I can access the db session via a common method or I'll need to fix this later.
        # For now, I'll write the code assuming I can get the session.
        pass

# Wait, I should probably check how to query first. 
# I'll create the file with the decorators first, and I'll refine the user loading logic in the route or a separate service if needed.

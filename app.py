from flask import (Flask)
from auth.auth import auth
from admin.admin import admin
from sessions.sessions import sessions
from member.member import member
from traniner.traniner import traniner

app = Flask(__name__)
app.secret_key = "admin123" 

# Registering blueprints
app.register_blueprint(admin)
app.register_blueprint(auth)
app.register_blueprint(member)
app.register_blueprint(sessions)
app.register_blueprint(traniner)

if __name__ == '__main__':
    app.run(debug=True)

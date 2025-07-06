from flask import Flask
from flask_login import LoginManager
from models import db
import auth, api

# دالة create_app تهيّئ تطبيق Flask،
# تضبط إعدادات الأمان وقاعدة البيانات وإدارة تسجيل الدخول، تسجّل البلوبرينتس (auth و API)، وتنشئ الجداول قبل تشغيل الخادم.

def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY='secret!123',
        SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:madness@localhost/dashboard',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    db.init_app(app)
    login = LoginManager(app)
    login.login_view = 'auth.login'
    login.user_loader(auth.load_user)
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)
    with app.app_context():
        db.create_all()
    return app

if __name__ == '__main__':
    create_app().run(debug=True)

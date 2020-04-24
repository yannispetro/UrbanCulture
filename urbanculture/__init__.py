from flask import Flask
from flask_bootstrap import Bootstrap

from .commands import create_tables
from .extensions import db
from .routes import main

def create_app(config_file='settings.py'):
    app = Flask(__name__)

    app.config.from_pyfile(config_file)
    app.config['SECRET_KEY'] = 'PleaseDontTellsdfkskdfsfowierk2o34wkefldlflpwef020wief3jfklmwenfpimd2'

    Bootstrap(app)

    db.init_app(app)

    app.register_blueprint(main)

    app.cli.add_command(create_tables)

    return app

# app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

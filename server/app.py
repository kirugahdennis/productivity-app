from flask import Flask, make_response
from flask_restful import Api
from flask_cors import CORS

from server.config import Config
from server.extensions import db, migrate, bcrypt


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # supports_credentials is required so the session cookie is sent
    # back and forth between the API and a frontend on another origin.
    CORS(app, supports_credentials=True)

    api = Api(app)

    # Import models so Flask-Migrate can see them when generating
    # migrations, and import routes here (after extensions are
    # initialized) to avoid circular imports.
    from server.models import User, JournalEntry  # noqa: F401
    from server.routes.auth import Signup, Login, Logout, CheckSession
    from server.routes.journal_entries import JournalEntryIndex, JournalEntryByID

    api.add_resource(Signup, "/signup")
    api.add_resource(Login, "/login")
    api.add_resource(Logout, "/logout")
    api.add_resource(CheckSession, "/check_session")

    api.add_resource(JournalEntryIndex, "/journal_entries")
    api.add_resource(JournalEntryByID, "/journal_entries/<int:id>")

    @app.route("/")
    def index():
        return make_response({"message": "Journal API is running"}, 200)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True, use_reloader=False)
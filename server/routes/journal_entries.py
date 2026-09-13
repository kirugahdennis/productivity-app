from flask import request
from flask_restful import Resource, abort
from marshmallow import ValidationError

from server.extensions import db
from server.models.journal_entry import JournalEntry
from server.schemas import journal_entry_schema, journal_entry_update_schema
from server.helpers import login_required, current_user

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50


def _get_owned_entry_or_404(entry_id, user):
    """Look up an entry by id and make sure it belongs to `user`.

    Returns a 404 (not 403) when the entry belongs to someone else, so
    that requests can't be used to probe which ids exist.
    """
    entry = db.session.get(JournalEntry, entry_id)
    if entry is None or entry.user_id != user.id:
        abort(404, message="Journal entry not found")
    return entry


class JournalEntryIndex(Resource):
    @login_required
    def get(self):
        user = current_user()

        try:
            page = max(int(request.args.get("page", 1)), 1)
        except (TypeError, ValueError):
            page = 1
        try:
            per_page = int(request.args.get("per_page", DEFAULT_PAGE_SIZE))
        except (TypeError, ValueError):
            per_page = DEFAULT_PAGE_SIZE
        per_page = max(1, min(per_page, MAX_PAGE_SIZE))

        query = JournalEntry.query.filter_by(user_id=user.id).order_by(
            JournalEntry.created_at.desc(), JournalEntry.id.desc()
        )
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "entries": [entry.to_dict() for entry in pagination.items],
            "meta": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total_pages": pagination.pages,
                "total_items": pagination.total,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            },
        }, 200

    @login_required
    def post(self):
        user = current_user()
        data = request.get_json() or {}

        try:
            valid = journal_entry_schema.load(data)
        except ValidationError as err:
            return {"errors": err.messages}, 422

        entry = JournalEntry(
            title=valid["title"],
            content=valid["content"],
            mood=valid.get("mood"),
            user_id=user.id,
        )

        try:
            db.session.add(entry)
            db.session.commit()
        except ValueError as err:
            db.session.rollback()
            return {"errors": [str(err)]}, 422

        return entry.to_dict(), 201


class JournalEntryByID(Resource):
    @login_required
    def get(self, id):
        user = current_user()
        entry = _get_owned_entry_or_404(id, user)
        return entry.to_dict(), 200

    @login_required
    def patch(self, id):
        user = current_user()
        entry = _get_owned_entry_or_404(id, user)

        data = request.get_json() or {}
        try:
            valid = journal_entry_update_schema.load(data)
        except ValidationError as err:
            return {"errors": err.messages}, 422

        try:
            for key, value in valid.items():
                setattr(entry, key, value)
            db.session.commit()
        except ValueError as err:
            db.session.rollback()
            return {"errors": [str(err)]}, 422

        return entry.to_dict(), 200

    @login_required
    def delete(self, id):
        user = current_user()
        entry = _get_owned_entry_or_404(id, user)

        db.session.delete(entry)
        db.session.commit()
        return {}, 204
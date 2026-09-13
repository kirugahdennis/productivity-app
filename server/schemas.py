from marshmallow import Schema, fields, validate

from server.models.journal_entry import MOODS


class SignupSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=1, max=80))
    password = fields.String(required=True, validate=validate.Length(min=6, max=128))


class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class JournalEntrySchema(Schema):
    """Used to validate incoming create/update payloads.

    `partial=True` is passed at PATCH time so callers can update a
    subset of fields.
    """

    title = fields.String(required=True, validate=validate.Length(min=1, max=120))
    content = fields.String(required=True, validate=validate.Length(min=1))
    mood = fields.String(required=False, allow_none=True, validate=validate.OneOf(MOODS))


signup_schema = SignupSchema()
login_schema = LoginSchema()
journal_entry_schema = JournalEntrySchema()
journal_entry_update_schema = JournalEntrySchema(partial=True)
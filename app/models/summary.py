"""Summary objects defined within Metadata objects."""
from . import db


# Summaries contained within Metadata:
class Summary(db.DynamicEmbeddedDocument):
    """Definition of the Summary class to be used in MongoEngine."""

    n_variables = db.IntField()
    pct_data = db.FloatField()

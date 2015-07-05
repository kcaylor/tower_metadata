from . import db


# Summaries contained within Metadata:
class Summary(db.DynamicEmbeddedDocument):

    n_variables = db.IntField()
    pct_data = db.FloatField()

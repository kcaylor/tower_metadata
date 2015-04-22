from mongoengine import *

MongoEngine()

class B(EmbeddedDocument):

    name = StringField(default='B')

    def clean(self):
        print "Cleaning up B"


class A(Document):

    name = StringField(default='A')
    embed = EmbeddedDocumentField(B)

    def clean(self):
        print "Cleaning up A"

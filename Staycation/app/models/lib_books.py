from app import db

class Book(db.Document):
    meta = {'collection': 'books'}  # name of my new collection
    title = db.StringField(required=True, max_length=150)
    authors = db.ListField(db.StringField(), required=True)
    genres = db.ListField(db.StringField())
    category = db.StringField(max_length=50)
    url = db.StringField(max_length=500)  # book cover image
    description = db.ListField(db.StringField())  # multiple paragraphs
    pages = db.IntField()
    available = db.IntField(default=0)
    copies = db.IntField(default=0)

    # Optional: method to check stock
    def is_available(self):
        return self.available > 0

    # Static methods to query
    @staticmethod
    def getBook(title):
        return Book.objects(title=title).first()

    @staticmethod
    def getAllBooks():
        return Book.objects()

    @staticmethod
    def createBook(title, authors, genres, category, url, description, pages, available, copies):
        return Book(
            title=title,
            authors=authors,
            genres=genres,
            category=category,
            url=url,
            description=description,
            pages=pages,
            available=available,
            copies=copies
        ).save()


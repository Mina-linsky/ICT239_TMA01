from app import db

class Book(db.Document):
    meta = {'collection': 'books'}  # defined name of the book collection

    #Book info
    title = db.StringField(required=True, max_length=200)
    category = db.StringField(max_length=50, required=True)
    url = db.StringField(max_length=500)
    pages = db.IntField(required=True, min_value=1)
    available = db.IntField(default=0, min_value=0)
    copies = db.IntField(default=1, min_value=1)

    # List fields
    genres = db.ListField(db.StringField(max_length=50))
    authors = db.ListField(db.StringField(max_length=100), required=True)
    description = db.ListField(db.StringField())

    def __str__(self):
        return f"{self.title} by {', '.join(self.authors)}"

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
        book = Book(
            title=title,
            authors=authors,
            genres=genres,
            category=category,
            url=url,
            description=description,
            pages=pages,
            available=available,
            copies=copies
        )
        return book.save()  # returns the saved Book instanc




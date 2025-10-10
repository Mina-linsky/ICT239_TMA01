from app import db

class Book(db.Document):
    meta = {'collection': 'books'}  # defined name of the book collection

    #Book info
    genres = db.ListField(db.StringField()) # List of str
    title = db.StringField(required=True, unique=True) # str (keeping required/unique for good measure)
    category = db.StringField() # str
    url = db.StringField() # str
    description = db.ListField(db.StringField()) # List of str
    authors = db.ListField(db.StringField(), required=True) # List of str (keeping required)
    pages = db.IntField() # int
    available = db.IntField(default=0) # int (keeping default for practical use)
    copies = db.IntField(default=1) # int (keeping default for practical use)

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
        return book.save()  # returns the saved Book instance

    



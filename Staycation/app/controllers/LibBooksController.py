from flask import Blueprint, render_template
from models.lib_books import Book

books_bp = Blueprint('books', __name__)

@books_bp.route('/')
@books_bp.route('/books')
def all_books():
    all_books = Book.getAllBooks()
    return render_template('books.html', panel="ALL BOOKS", all_books=all_books)

@books_bp.route("/viewBookDetail/<title>")
def view_book_detail(title):
    the_book = Book.getBook(title=title)
    return render_template('bookDetail.html', panel="Book Detail", book=the_book)
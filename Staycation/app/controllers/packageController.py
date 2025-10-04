from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, request, redirect, render_template, url_for

from models.forms import BookForm

from models.users import User
from models.package import Package
from models.lib_books import Book
from app.books import all_books

package = Blueprint('packageController', __name__)

@package.route('/')
@package.route('/BookTitles')
def book_titles():
    # all_books = Book.getAllBooks()
    return render_template('books.html', panel="BOOK TITLES", all_books=all_books)

@package.route("/viewPackageDetail/<hotel_name>")
def viewPackageDetail(hotel_name):
    the_package = Package.getPackage(hotel_name=hotel_name)
    return render_template('packageDetail.html', panel="Package Detail", package=the_package)

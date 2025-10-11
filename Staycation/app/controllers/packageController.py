from flask import Blueprint, request, render_template, redirect, url_for, flash 
from datetime import datetime, timedelta
import random
from flask_login import current_user, login_required
from bson import ObjectId
from datetime import datetime
from models.lib_books import Book
from app.models.Loan import Loan
from models.users import User
from app.books import all_books    # still needed for DB initialization
# from app.books import all_books #question 2a to populate the books

package = Blueprint('packageController', __name__)

# Populate MongoDB from all_books if collection empty
def initialize_books():
    if Book.objects.count() == 0:
        for b in all_books:
            Book(**b).save()
        print("✅ MongoDB populated with books from all_books.")
    else:
        print("✅ Book collection already populated.")


@package.route('/')
@package.route("/BookTitles")
def book_titles():
    selected_category = request.args.get('category', 'All')

    # ✅ Fetch books from MongoDB
    if selected_category == 'All':
        books = Book.objects()  # all documents
    else:
        books = Book.objects(category=selected_category)

    # ✅ Sort alphabetically
    sorted_books = sorted(books, key=lambda b: b.title.lower())

    # ✅ Generate short description
    for book in sorted_books:
        desc_list = getattr(book, 'description', [])
        if len(desc_list) > 1:
            book.short_description = f"{desc_list[0]}\n\n{desc_list[-1]}"
        elif desc_list:
            book.short_description = desc_list[0]
        else:
            book.short_description = "No description available."

    return render_template(
        'books.html',
        panel="BOOK TITLES",
        all_books=sorted_books,
        selected_category=selected_category
    )

@package.route("/viewBookDetail/<book_title>")
def viewBookDetail(book_title):
    # Find by title (case-insensitive)
    book = Book.objects(title__iexact=book_title).first()

    if not book:
        return render_template('error.html', message="Book not found."), 404

    return render_template(
        'BookDetailsPage.html',
        panel="BOOK DETAIL",
        book=book
    )

@package.route('/make_loan/<book_id>', methods=['GET', 'POST'])
def make_loan(book_id):
    if not current_user.is_authenticated:
        flash("Please login or register first to get an account", "warning")
        return redirect(url_for('auth.login'))
    
    try:
        book = Book.objects(id=book_id).first()
        if not book:
            flash("Book not found", "error")
            return redirect(url_for('packageController.book_titles'))

        if request.method == 'POST':
            # This should be in your make_loan route:
            borrow_date = datetime.now() + timedelta(days=random.randint(10, 20))
            
            loan, msg = Loan.create_loan(current_user.id, book.id, borrow_date)
            
            if loan:
                flash("Loan successfully created!", "success")  # This will show on book_titles page
                return redirect(url_for('packageController.book_titles'))
            else:
                # Check if it's the "already borrowed" error
                if "already have an active loan" in msg:
                    flash("You already borrowed this book~!", "warning")
                else:
                    flash(msg, "error")
                return render_template('make_loan.html', book=book)

        return render_template('make_loan.html', book=book)
        
    except Exception as e:
        print(f"❌ ERROR in make_loan: {str(e)}")
        flash("An unexpected error occurred while processing your loan", "error")
        return redirect(url_for('packageController.book_titles'))

@package.route('/return_loan/<loan_id>')
def return_loan(loan_id):
    if not current_user.is_authenticated:
        flash("Please login first", "warning")
        return redirect(url_for('auth.login'))
    
    loan = Loan.get_loan_by_id(loan_id)
    if not loan:
        flash("Loan not found", "error")
        return redirect(url_for('packageController.userLoanStatus'))
    
    if loan.member.id != current_user.id:
        flash("You can only return your own loans", "error")
        return redirect(url_for('packageController.userLoanStatus'))
    
    result = loan.return_book()
    flash(result, "success" if "successfully" in result else "error")
    return redirect(url_for('packageController.userLoanStatus'))

@package.route('/renew_loan/<loan_id>')
def renew_loan(loan_id):
    if not current_user.is_authenticated:
        flash("Please login first", "warning")
        return redirect(url_for('auth.login'))
    
    loan = Loan.get_loan_by_id(loan_id)
    if not loan:
        flash("Loan not found", "error")
        return redirect(url_for('packageController.userLoanStatus'))
    
    if loan.member.id != current_user.id:
        flash("You can only renew your own loans", "error")
        return redirect(url_for('packageController.userLoanStatus'))
    
    result = loan.renew()
    flash(result, "success" if "successfully" in result else "error")
    return redirect(url_for('packageController.userLoanStatus'))

@package.route('/delete_loan/<loan_id>')
def delete_loan(loan_id):
    if not current_user.is_authenticated:
        flash("Please login first", "warning")
        return redirect(url_for('auth.login'))
    
    loan = Loan.get_loan_by_id(loan_id)
    if not loan:
        flash("Loan not found", "error")
        return redirect(url_for('packageController.userLoanStatus'))
    
    if loan.member.id != current_user.id:
        flash("You can only delete your own loans", "error")
        return redirect(url_for('packageController.userLoanStatus'))
    
    result = loan.delete_loan()
    flash(result, "success" if "successfully" in result else "error")
    return redirect(url_for('packageController.userLoanStatus'))


@package.route('/userLoanStatus')
def userLoanStatus():
    if not current_user.is_authenticated:
        flash("Please login to view your loans", "warning")
        return redirect(url_for('auth.login'))
    
    loans = Loan.get_user_loans(current_user.id)
    
    return render_template('user_Loan.html', 
                         loans=loans,
                         today=datetime.now(),
                         timedelta=timedelta)


# @package.route('/')
# @package.route("/BookTitles")
# # def book_titles():
# #    # all_books = Book.getAllBooks()
# #     return render_template('books.html', panel="BOOK TITLES", all_books=all_books)

# def book_titles():
#     # Get category from query parameter (default = All)
#     selected_category = request.args.get('category', 'All')

#     # ✅ Filter by category if not 'All'
#     if selected_category == 'All':
#         filtered_books = all_books
#     else:
#         filtered_books = [b for b in all_books if b['category'] == selected_category]

#     # ✅ Sort filtered books alphabetically by title
#     sorted_books = sorted(filtered_books, key=lambda b: b['title'].lower())

#     # ✅ Keep only the first and last paragraphs of description
#     for book in sorted_books:
#         desc_list = book.get('description', [])
#         if len(desc_list) > 1:
#             short_desc = f"{desc_list[0]}\n\n{desc_list[-1]}"
#         elif desc_list:
#             short_desc = desc_list[0]
#         else:
#             short_desc = "No description available."
#         book['short_description'] = short_desc

#     return render_template(
#         'books.html',
#         panel="BOOK TITLES",
#         all_books=sorted_books,
#         selected_category=selected_category
#     )

    

# @package.route("/viewBookDetail/<book_title>")
# def viewBookDetail(book_title):
#     # Find the book by title
#     the_book = next((b for b in all_books if b['title'] == book_title), None)
    
#     if not the_book:
#         return render_template('error.html', message="Book not found."), 404

#     return render_template(
#         'BookDetailsPage.html',
#         panel="BOOK DETAIL",
#         book=the_book
#     )





# from flask_login import login_user, login_required, logout_user, current_user
# from flask import Blueprint, request, redirect, render_template, url_for

# from models.forms import BookForm

# from models.users import User
# from models.package import Package
# from models.lib_books import Book
# from app.books import all_books #question 2a to populate the books

# package = Blueprint('packageController', __name__)

# @package.route('/')
# @package.route("/BookTitles")
# # def book_titles():
# #    # all_books = Book.getAllBooks()
# #     return render_template('books.html', panel="BOOK TITLES", all_books=all_books)

# def book_titles():
#     # Get category from query parameter (default = All)
#     selected_category = request.args.get('category', 'All')

#     # ✅ Filter by category if not 'All'
#     if selected_category == 'All':
#         filtered_books = all_books
#     else:
#         filtered_books = [b for b in all_books if b['category'] == selected_category]

#     # ✅ Sort filtered books alphabetically by title
#     sorted_books = sorted(filtered_books, key=lambda b: b['title'].lower())

#     # ✅ Keep only the first and last paragraphs of description
#     for book in sorted_books:
#         desc_list = book.get('description', [])
#         if len(desc_list) > 1:
#             short_desc = f"{desc_list[0]}\n\n{desc_list[-1]}"
#         elif desc_list:
#             short_desc = desc_list[0]
#         else:
#             short_desc = "No description available."
#         book['short_description'] = short_desc

#     return render_template(
#         'books.html',
#         panel="BOOK TITLES",
#         all_books=sorted_books,
#         selected_category=selected_category
#     )

    

# @package.route("/viewBookDetail/<book_title>")
# def viewBookDetail(book_title):
#     # Find the book by title
#     the_book = next((b for b in all_books if b['title'] == book_title), None)
    
#     if not the_book:
#         return render_template('error.html', message="Book not found."), 404

#     return render_template(
#         'BookDetailsPage.html',
#         panel="BOOK DETAIL",
#         book=the_book
#     )
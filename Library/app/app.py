from flask_login import login_required, current_user
from flask import render_template, request, jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

import csv
import io
import datetime as dt
import os

from app import create_app, db, login_manager
app = create_app()

from app.models.package import Package
from app.models.book import Booking
from app.models.users import User
from app.models.lib_books import Book
from app.models.Loan import Loan

@app.route('/base')
def show_base():
    return render_template('books.html')


@app.route("/NewBook", methods=['GET', 'POST'])
@login_required
def add():
    genres = [
        "Animals", "Business", "Comics", "Communication", "Dark Academia",
        "Emotion", "Fantasy", "Fiction", "Friendship", "Graphic Novels", "Grief",
        "Historical Fiction", "Indigenous", "Inspirational", "Magic", "Mental Health",
        "Nonfiction", "Personal Development", "Philosophy", "Picture Books", "Poetry",
        "Productivity", "Psychology", "Romance", "School", "Self Help"
    ]

    if request.method == 'GET':
        return render_template(
            "Add_Book.html", 
            name=current_user.name, 
            panel="Upload",
            genres=genres
        )

    elif request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        url = request.form.get('url')
        description = request.form.get('description')  # ✅ Get description from form
        genres_selected = request.form.getlist('genres')

        # Collect authors from author1..author5 fields and filter out empty strings
        authors = []
        for i in range(1, 6):
            a = request.form.get(f'author{i}')
            if a and a.strip():
                authors.append(a.strip())

        if not authors:
            flash("Please enter at least one author.", "danger")
            return render_template(
                "Add_Book.html",
                name=current_user.name,
                panel="Upload",
                genres=genres
            )

        # Get pages and copies, default to 0 and 1 if not provided
        pages = request.form.get('pages')
        copies = request.form.get('copies')

        try:
            pages = int(pages) if pages else 0
        except ValueError:
            flash("Pages must be a number.", "danger")
            return render_template(
                "Add_Book.html",
                name=current_user.name,
                panel="Upload",
                genres=genres
            )

        try:
            copies = int(copies) if copies else 1
        except ValueError:
            flash("Copies must be a number.", "danger")
            return render_template(
                "Add_Book.html",
                name=current_user.name,
                panel="Upload",
                genres=genres
            )

        # ✅ Handle description safely
        description_list = []
        if description:
            # Split into paragraphs if user entered multiple lines
            description_list = [line.strip() for line in description.split('\n') if line.strip()]

        # ✅ Create and save the book
        new_book = Book(
            title=title,
            authors=authors,
            genres=genres_selected,
            category=category,
            url=url,
            description=description_list,  # ✅ include description
            pages=pages,
            copies=copies,
            available=copies
        )
        new_book.save()

        # ✅ Return form with success message
        return render_template(
            "Add_Book.html",
            name=current_user.name,
            panel="Upload",
            genres=genres,
            success="Book successfully added~!"
        )


@app.route("/changeAvatar")
@login_required
def changeAvatar():
    basedir = os.path.abspath(os.path.dirname(__file__))
    subfolder_path = os.path.join('assets', 'img/avatar')
    subfolder_abs_path = os.path.join(basedir, subfolder_path)
    
    files = []
    for filename in os.listdir(subfolder_abs_path):
        path = os.path.join(subfolder_abs_path, filename)
        if os.path.isfile(path):
            files.append(filename)
    return render_template("changeAvatar.html", filenames=files, panel="Change Avatar") 


@app.route("/chooseAvatar", methods=['POST'])
@login_required
def chooseAvatar():
    chosenPath = request.json['path']
    print('chosen path: ', chosenPath)
  
    basedir = os.path.abspath(os.path.dirname(__file__))
    subfolder_path = os.path.join('assets', 'img/avatar')
    subfolder_abs_path = os.path.join(basedir, subfolder_path)
    
    filename = chosenPath.split('/')[-1]
    User.addAvatar(current_user, filename)
    
    return jsonify(path=chosenPath)

@app.route("/userLoanStatus")
def userLoans():
    if not current_user.is_authenticated:
        flash("Please login to view your loans", "warning")
        return redirect(url_for('auth.login'))
    
    loans = Loan.get_user_loans(current_user.id)
    
    # Convert today to datetime for consistent comparison
    today_datetime = datetime.now()
    
    return render_template('user_Loan.html', 
                         loans=loans,
                         today=today_datetime,  # Keep as datetime
                         timedelta=timedelta)

if __name__ == '__main__':
    app.run(debug=True)


# Library-Service-Project
**Library Service Project** is a REST API for managing books and borrows in the library.


## Installing using GitHub

Python3 must be already installed

``` shel
git clone https://github.com/AndreiVed/Library-Service-Project
cd Library-Service-Project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 
```

## Getting access

* create user via /users/register/
* get access token via /users/token/

## Features

* JWT authenticated
* Admin panel
* Documentation is located at doc/swagger/
* Information of test coverage is located at htmlcov/index.html
* Create user and managing user`s info
* Managing books (only for admin)
* Creating borrowings book (only authenticated users)
* Filtering Borrowings List by is_active and user_id (for admins) fields
* Each non-admin can see only their own borrowings
* If user borrows book, book`s inventory decreases by 1 
* If user returns book, book`s inventory increases by 1 
* User can not borrow book, if book`s inventory is equal 0


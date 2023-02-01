# Blog: ALL ABOUT DATA SCIENCE
####  <URL HERE>
#### Description: this is an online open platform where readers find dynamic thinking, and experts can share their unique writing/ideas on the data science field.
### Below are the description of the files I've created in my project.
1.	helper.py
Included apology and login_required function. I also added another function called strip_invalid_html which is to extract the unnecessary html tags from ckeditor before the data is enter into SQL.

2.	app.py
Atop the file are a bunch of imports, including CS50’s SQL module, flask modules and a few helper functions.
There are lots of webforms involved in my project. In order to make it easy, I decided to adopt the popular wtf forms and bootstrap extensions of flask. To instantiate the forms, I created 3 classes called LoginForm, RegisterForm and PostForm which inherited the properties from FlaskForm.
    - about route renders “about.html”.
    - contact route renders “contact.html”.
    - edit-post route first checks the post id which is then used to extract data from sql server. It will auto-populate the fields taking the data from sql table blogs, so that users don’t have to re-enter the contents. After that it renders “make-post.html” if it’s a GET request, and “post.html” if it’s a POST request and the validation is passed.  There’s also a flash message “Post has been updated! Meanwhile, SQL server blogs will be updated with the new contents.
    - delete-post route allows user to delete post. Currently, it doesn’t have the functionality to only allow user to edit or delete their own posts but I’ll add that at a later stage.
    - index route renders the homepage which lists all the blogs.
    - login route renders “login.html” if uses comes via the GET request. If it’s POST request, the function checks the username and hash password against the sql and return apology if failure. If successful, uses will be taken to the homepage and see a flash message “You are loggin in!”
    - logout route simply clears session, effectively logging a user out.
    - new-post renders “make-post.html” if it’s a GET request. it will say “edit post” if user comes from the edit-post route, or “new post” if user comes from the new-post route. If it’s POST request and the validation is passed, blog data will be inserted into the table blogs, and uses will be taken to the homepage and see a flash message “You published a new post!”
    - register route will simply render “register.htm” if it’s a GET request. If users come via POST request, the server will validate if user exists and password matches the confirmation and then insert new user into sql. It will also remember the session and redirect users to the homepage with a flash message “You are signed up!”
    - show-post route takes user to the individual post they clicked on in the homepage. It only accepts the default GET request.

3. blog.db
It includes 2 tables, users and blogs.

4. html templates
    - apology.html
    apology function in helpers.py took two arguments: message, which was passed to “apology.html” as the value of bottom, and, optionally, code, which was passed as the value of top.

    - layout.html
    It’s based on a bootstrap template downloaded online, but I added some jinja template which allows users to only see login and signup if they haven’t, and see all the menu items if they are logged in.

    - about.html
    It gives a brief introduction of the website which is now filled with Lorem ipsum.

    - contact.html
    It is a simple form. Once users filled in the information, it will be a post request to the server , and user see the header is changed to  “Successfully sent your message” .

    - make-post.html
    It will say “edit post” in the page header if user comes from the edit-post route, or “new post” if user comes from the new-post route.  If it’s edit more, it will auto-populate the fields taking the data from sql table blogs, so that users don’t have to re-enter the contents.

    - index.html
    I added jinja template to capture username and display it in the title. There’s also a for loop which populate all posts in the sql table blogs.

    - login.html
    It renders the login form.

    - register.html
    It renders the logout form.

    - post.html
    It generates the individual post uses clicked on.


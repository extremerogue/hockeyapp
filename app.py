from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import smtplib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///friends.db'
#Initialize the database
db=SQLAlchemy(app)

#Create db model
class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    #Create a function to return a string when we add something
    def __repr__(self):
        return '<Name %r>' %self.id

subscribers = []

@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    friend_to_delete = Friends.query.get_or_404(id)
    try:
        db.session.delete(friend_to_delete)
        db.session.commit()
        return redirect('/friends')
    except:
        return "There was a problem deleting that friend"

@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    friend_to_update =  Friends.query.get_or_404(id)
    if request.method == "POST":
        friend_to_update.name =  request.form['name']
        try:
            db.session.commit()
            return redirect('/friends')
        except:
            return "There was a problem updating that friend..."

    else:
        return render_template('update.html', friend_to_update=friend_to_update)

@app.route('/friends', methods=['POST', 'GET'])
def friends():
    title = " My Friend List"

    if request.method == 'POST':
        friend_name = request.form['name']
        new_friend = Friends(name=friend_name)

        # Push to database
        try:
            db.session.add(new_friend)
            db.session.commit()
            return redirect('/friends')
        except:
            return "There was an error adding your friend..."

    else:
        friends = Friends.query.order_by(Friends.date_created)
        return render_template("friends.html", title=title, friends=friends)


@app.route('/')
def index():
    #title = "Kage Howard's Portfolio"
    return render_template("index.html")

@app.route('/about')
def about():
    names = ["John", "Mary", "Wes", "Sally"]
    title = " About John Elder !!!"
    return render_template("about.html", names=names, title=title)

@app.route('/subscribe')
def subscribe():
    title = "Subscribe to My Email Newsletter"
    return render_template("subscribe.html", title=title)

@app.route('/form', methods=["POST"])
def form():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")

    message = "You have been subscribed to my email newletter"
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("nagadagadin@gmail.com", "enterpasswordhere")
    server.sendmail("nagadagadin@gmail.com", email, message)

    if not first_name or not last_name or not email:
        error_statement = "All From Fields Required..."
        return render_template("subscribe.html",error_statement=error_statement,
                               first_name=first_name, last_name=last_name, email=email)

    subscribers.append(f"{first_name} {last_name} | {email}")
    title = "Thank You!"
    return render_template("form.html", title=title, subscribers=subscribers)

if __name__ == "__main__":  # on running python app.py
    app.run(debug=True)  # run the flask app
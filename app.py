from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import smtplib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hockey.db'
#Initialize the database
db=SQLAlchemy(app)

#Create db model   Note: Classes map to tables in SQLAlchemy
class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    #Create a function to return a string when we add something
    def __repr__(self):
        return '<Name %r>' %self.id

class Coaches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    team_id = db.Column(db.Integer)

    #Create a function to return a string when we add something
    def __repr__(self):
        return '<Name %r>' %self.id

class Stations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    practice_id = db.Column(db.Integer)
    coach_id = db.Column(db.Integer)
    coach_name = db.Column(db.String(50))

    #Create a function to return a string when we add something
    def __repr__(self):
        return '<Name %r>' %self.id        

class Practices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    team_id = db.Column(db.Integer)

    #Create a function to return a string when we add something
    def __repr__(self):
        return '<Name %r>' %self.id

@app.route('/')
def index():
    teams = Teams.query.all()
    practices = Practices.query.all()
    stations = Stations.query.all()

    return render_template("index.html", teams=teams, practices=practices, stations=stations)

@app.route('/about')
def about():
    names = ["John", "Mary", "Wes", "JimmyZ"]
    title = " About John Elder !!!"
    return render_template("about.html", names=names, title=title)

@app.route('/coaches', methods=['POST', 'GET'])
def coaches():
    title = "Coaches Roster"

    if request.method == 'POST':
        data = request.form
        coach_name = data['name']
        team_id_str = data['team_id'] #team_id
        team_id = int(team_id_str)
        new_coach = Coaches(name=coach_name,team_id=team_id)
        #new_coach is the object created from Coaches. We will add the object.name and object.team_id)

        # Push to database
        try:
            db.session.add(new_coach)
            db.session.commit()
            return redirect('/coaches')
        except:
            return "There was an error adding your coach..."

    else:
        coaches = Coaches.query.order_by(Coaches.date_created)
        return render_template("manageteam.html", title=title, coaches=coaches)


@app.route('/teams', methods=['POST', 'GET'])
def teams():
    title = "Teams"

    if request.method == 'POST':
        team_name = request.form['name']

        if team_name:
        # return team_name+team_location
        
                new_team = Teams(name=team_name)  #Teams is the model (aka: Table in the DB)

                # Push to database
                try:
                    db.session.add(new_team)
                    db.session.commit()
                    return redirect('/teams')
                except:
                    return "There was an error adding your team..."
        else:
            error_string = "Please give the team a name."
            teams = Teams.query.order_by(Teams.date_created)
            return render_template("teams.html", title=title, teams=teams, error_string=error_string)

    else:
        teams = Teams.query.order_by(Teams.date_created)
        return render_template("teams.html", title=title, teams=teams)

@app.route('/coachadd/<int:team_id>', methods=['POST', 'GET'])
def coachadd(team_id):
    coaches = Coaches.query.filter(Coaches.team_id == team_id)
    team = Teams.query.get_or_404(team_id)
    practices = Practices.query.filter(Practices.team_id == team_id)

    if request.method == 'POST':
        # Add a New Coach
        coach_name = request.form['name']
        new_coach = Coaches(name=coach_name, team_id=team_id)

        if coach_name:
            # Push new coach to database
            try:
                db.session.add(new_coach)
                db.session.commit()

                return render_template('manageteam.html', team=team, coaches=coaches, practices=practices)
            except:
                return "There was an error adding your coach"

        else: 
            coach_error = "Please give the coach a name."
            return render_template('manageteam.html', team=team, coaches=coaches, practices=practices, coach_error=coach_error)

    else:
        return render_template('manageteam.html', team=team, coaches=coaches, practices=practices)


@app.route('/practiceadd/<int:team_id>', methods=['POST', 'GET'])
def practiceadd(team_id):
    coaches = Coaches.query.filter(Coaches.team_id == team_id)
    team = Teams.query.get_or_404(team_id)
    practices = Practices.query.filter(Practices.team_id == team_id)

    if request.method == 'POST':
        # Add a New Practice
        practice_name = request.form['name']
        new_practice = Practices(name=practice_name,team_id=team_id)

        if practice_name:
            # Push new practice to database
            try:
                db.session.add(new_practice)
                db.session.commit()
                return render_template('manageteam.html', team=team, coaches=coaches, practices=practices)
            except:
                return "There was an error adding your practice"

        else:
            practice_error = "Please give the practice a name."
            return render_template('manageteam.html', team=team, coaches=coaches, practices=practices, practice_error=practice_error)
    
    else:
        return render_template('manageteam.html', team=team, coaches=coaches, practices=practices)

@app.route('/stationadd/<int:practice_id>', methods=['POST', 'GET'])
def stationadd(practice_id):
    stations = Stations.query.filter(Stations.practice_id == practice_id)
    practice = Practices.query.get_or_404(practice_id)
    team_id = practice.team_id
    team = Teams.query.get_or_404(team_id)
    coaches = Coaches.query.filter(Coaches.team_id == team_id )
 
    if request.method == 'POST':
        # Add a New Stations
        stations_name = request.form['name']
        new_stations = Stations(name=stations_name, practice_id=practice_id)

        if stations_name:

            # Push new stations to database
            try:
                db.session.add(new_stations)
                db.session.commit()
                return render_template('managepractice.html', team=team, practice=practice, stations=stations, coaches=coaches)
            except:
                return "There was an error adding your pratice"

        else:
            station_error = "Please give the station a name."
            return render_template('managepractice.html', team=team, practice=practice, stations=stations, coaches=coaches, station_error=station_error)

    else:
        return render_template('managepractice.html', team=team, practice=practice, stations=stations, coaches=coaches)



@app.route('/manageteam/<int:team_id>', methods=['POST', 'GET'])
def manageteam(team_id):
    team = Teams.query.get_or_404(team_id)
    coaches = Coaches.query.filter(Coaches.team_id == team_id)
    practices = Practices.query.filter(Practices.team_id == team_id)
    
    return render_template('manageteam.html',team=team, coaches=coaches, practices=practices)

@app.route('/managepractice/<int:team_id>/<int:practice_id>', methods=['POST', 'GET'])
def managepractice(team_id, practice_id):
    title = "Manage Practice"
    team = Teams.query.get_or_404(team_id)
    practice = Practices.query.get_or_404(practice_id)
    stations = Stations.query.filter(Stations.practice_id == practice_id)
    coaches = Coaches.query.filter(Coaches.team_id == team_id )
    
    return render_template('managepractice.html',title=title, team=team, practice=practice, stations=stations, coaches=coaches)

@app.route('/assigncoachtostation/<int:coach_id>/<int:station_id>', methods=['POST', 'GET'])
def assigncoachtostation(coach_id,station_id):
    station = Stations.query.get_or_404(station_id)
    station.coach_id = coach_id
    coach = Coaches.query.get_or_404(coach_id)
    station.coach_name = coach.name
    
    practice_id = station.practice_id
    practice = Practices.query.get_or_404(practice_id)
    team_id = practice.team_id
    team = Teams.query.get_or_404(team_id)
    stations = Stations.query.filter(Stations.practice_id == practice_id)
    coaches = Coaches.query.filter(Coaches.team_id == team_id )


    if request.method == 'POST':
        try:
            db.session.commit()
            return render_template('managepractice.html', team=team, practice=practice, stations=stations, coaches=coaches)
        except:
            return "There was an error updating a coach to your station"

    else:
        return render_template('managepractice.html', team=team, practice=practice, stations=stations, coaches=coaches)   


@app.route('/stationupdate/<int:station_id>', methods=['POST', 'GET'])
def stationupdate(station_id):
    station_to_update =  Stations.query.get_or_404(station_id)
    practice_id = station_to_update.practice_id
    practice = Practices.query.get_or_404(practice_id)
    team_id = practice.team_id
    team = Teams.query.get_or_404(team_id)
    stations = Stations.query.filter(Stations.practice_id == practice_id)
    coaches = Coaches.query.filter(Coaches.team_id == team_id )

    if request.method == "POST":
        station_to_update.name = request.form['name']
        try:
            db.session.commit()
            return render_template('managepractice.html', team=team, practice=practice, stations=stations, coaches=coaches)
        except:
            return "There was a problem updating that coach..."
    else:
        return render_template('stationupdate.html', station_to_update=station_to_update)

@app.route('/stationdelete/<int:station_id>', methods=['POST', 'GET'])
def stationdelete(station_id):
    station_to_delete = Stations.query.get_or_404(station_id)
    practice_id = station_to_delete.practice_id
    practice = Practices.query.get_or_404(practice_id)
    team_id = practice.team_id
    team = Teams.query.get_or_404(team_id)
    stations = Stations.query.filter(Stations.practice_id == practice_id)
    coaches = Coaches.query.filter(Coaches.team_id == team_id )

    try:
        db.session.delete(station_to_delete)
        db.session.commit()
        return render_template('managepractice.html', team=team, practice=practice, stations=stations, coaches=coaches)
    except:
        return "There was a problem deleting that station"        


@app.route('/coachupdate/<int:id>', methods=['POST', 'GET'])
def coachupdate(id):
    coach_to_update =  Coaches.query.get_or_404(id)
    team_id = coach_to_update.team_id
    if request.method == "POST":
        coach_to_update.name =  request.form['name']
        try:
            db.session.commit()
            return redirect('/manageteam/%r' %team_id)
        except:
            return "There was a problem updating that coach..."
    else:
        return render_template('coachupdate.html', coach_to_update=coach_to_update)


@app.route('/teamupdate/<int:id>', methods=['POST', 'GET'])
def teamupdate(id):
    team_to_update =  Teams.query.get_or_404(id)
    if request.method == "POST":
        team_to_update.name =  request.form['name']
        try:
            db.session.commit()
            return redirect('/teams')
        except:
            return "There was a problem updating that team..."
    else:
        return render_template('teamupdate.html', team_to_update=team_to_update)

@app.route('/practiceupdate/<int:id>', methods=['POST', 'GET'])
def practiceupdate(id):
    practice_to_update =  Practices.query.get_or_404(id)
    team_id = practice_to_update.team_id
    if request.method == "POST":
        practice_to_update.name =  request.form['name']
        try:
            db.session.commit()
            return redirect('/manageteam/%r' %team_id)
        except:
            return "There was a problem updating that practice..."
    else:
        return render_template('practicesupdate.html', practice_to_update=practice_to_update)


@app.route('/teamdelete/<int:id>', methods=['POST', 'GET'])
def teamdelete(id):
    team_to_delete = Teams.query.get_or_404(id)
    try:
        db.session.delete(team_to_delete)
        db.session.commit()
        return redirect('/teams')
    except:
        return "There was a problem deleting that team"

@app.route('/coachdelete/<int:id>', methods=['POST', 'GET'])
def coachdelete(id):
    coach_to_delete = Coaches.query.get_or_404(id)
    team_id = coach_to_delete.team_id
    try:
        db.session.delete(coach_to_delete)
        db.session.commit()
        return redirect('/manageteam/%r' %team_id)
    except:
        return "There was a problem deleting that coach"

@app.route('/practicedelete/<int:id>', methods=['POST', 'GET'])
def practicedelete(id):
    practice_to_delete = Practices.query.get_or_404(id)
    team_id = practice_to_delete.team_id
    try:
        db.session.delete(practice_to_delete)
        db.session.commit()
        return redirect('/manageteam/%r' %team_id)
    except:
        return "There was a problem deleting that team"

if __name__ == "__main__":  # on running python app.py
    db.create_all()
    app.run(debug=True)  # run the flask app
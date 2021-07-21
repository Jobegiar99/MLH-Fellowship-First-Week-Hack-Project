from os.path import join, dirname, realpath
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, send_from_directory, request, session
from dotenv import load_dotenv
from datetime import date
from app.python.components.factory import Factory
from app.python.components.adminCheck import AdminCheck
from PIL import Image as IMG
from werkzeug.utils import secure_filename

load_dotenv()
app = Flask(__name__)


UPLOAD_FOLDER = join(dirname(realpath(__file__)), "static/img")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio_post.sqlite3"
app.config["SQLALCHEMY_BINDS"] = {"projects": "sqlite:///portfolio_project.sqlite3"}

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = "dljsaklqk24e21cjn!Ew@@dsa5"

db = SQLAlchemy(app)


class Post(db.Model):
    __tablename__ = "post"
    id = db.Column("postID", db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String())
    content = db.Column(db.String())
    date = db.Column(db.Date())

    def __init__(self, title, content, date):
        self.title = title
        self.content = content
        self.date = date


class Project(db.Model):
    __bind_key__ = "projects"
    id = db.Column("projectID", db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String())
    shortDescription = db.Column(db.String(35))
    gif = db.Column(db.String())
    videoURL = db.Column(db.String())
    description = db.Column(db.String())
    githubURL = db.Column(db.String())
    demoURL = db.Column(db.String())

    def __init__(
        self, name, shortDescription, gif, videoURL, description, githubURL, demoURL
    ):
        self.name = name
        self.shortDescription = shortDescription
        self.gif = gif
        self.videoURL = videoURL
        self.description = description
        self.githubURL = githubURL
        self.demoURL = demoURL


db.create_all()
db.session.commit()


@app.route("/")
def index():
    return render_template("index.html", title="Jobegiar99", url=os.getenv("URL"))


@app.route("/projects", methods=["GET", "POST"])
def projects():
    return Factory().createProjectPreview(Project.query.all())


@app.route("/aboutMe")
def character():
    return render_template("character.html", url=os.getenv("URL"))


@app.route("/addProjectForm")
def addProjectForm():
    return render_template("addProject.html")


@app.route("/createProject", methods=["GET", "POST"])
def createProject():
    if request.method == "POST":
        name = request.form["projectName"]
        shortDescription = request.form["projectShortDescription"]
        gif = request.files["projectGIF"]
        videoURL = request.form["projectVideoURL"]
        description = request.form["projectDescription"]
        githubURL = request.form["projectGithubURL"]
        demoURL = request.form["projectDemoURL"]
        gifName = gif.filename.replace(" ", "_")
        gif.filename = gifName
        gif.save(os.path.join(UPLOAD_FOLDER, secure_filename(gif.filename)))

        project = Project(
            name, shortDescription, gifName, videoURL, description, githubURL, demoURL
        )
        db.session.add(project)
        db.session.commit()
        return projects()
    return index()


@app.route("/projectBigView", methods=["GET", "POST"])
def projectBigView():
    projectName = request.args.get("projectName")
    videoURL = request.args.get("videoURL")
    description = request.args.get("description")
    githubURL = request.args.get("githubURL")
    demoURL = request.args.get("demoURL")

    return render_template(
        "projectBigView.html",
        projectName=projectName,
        projectVideoUrl=videoURL,
        projectDescription=description,
        githubURL=githubURL,
        demoURL=demoURL,
    )


@app.route("/adminCheckProjects", methods=["GET", "POST"])
def adminCheckProjects():

    session["projectID"] = int(request.args.get("id"))
    session["projectOption"] = request.args.get("whatToDo")
    return render_template("adminCheck.html")


@app.route("/adminCheckProjectsHelper", methods=["GET", "POST"])
def adminCheckProjectsHelper():
    option = session.get("projectOption", None)

    if option == "delete":
        pID = session.get("projectID", None)
        Project.query.filter_by(id=pID).delete()
        db.session.commit()
        return index()

    elif option == "edit":

        pID = session.get("projectID", None)
        project = Project.query.get(pID)
        name = project.name
        shortDesc = project.shortDescription
        desc = project.description

        return render_template(
            "editProject.html",
            projectName=name,
            shortDescription=shortDesc,
            videoURL=project.videoURL,
            longDescription=desc,
            githubURL=project.githubURL,
            demoURL=project.demoURL,
        )

    else:
        return render_template("addProject.html")


@app.route("/updateProject", methods=["GET", "POST"])
def updateProject():
    if request.method == "POST":
        pID = session.get("projectID", None)

        name = request.form["projectName"]
        shortDescription = request.form["projectShortDescription"]
        gif = request.files["projectGIF"]
        videoURL = request.form["projectVideoURL"]
        description = request.form["projectDescription"]
        githubURL = request.form["projectGithubURL"]
        demoURL = request.form["projectDemoURL"]
        gifName = gif.filename.replace(" ", "_")
        filename = gifName
        gif.save(os.path.join(UPLOAD_FOLDER, secure_filename(gif.filename)))

        Project.query.filter_by(id=pID).update(
            {
                "name": name,
                "shortDescription": shortDescription,
                "gif": gifName,
                "videoURL": videoURL,
                "description": description,
                "githubURL": githubURL,
                "demoURL": demoURL,
            }
        )

        db.session.commit()

    return index()

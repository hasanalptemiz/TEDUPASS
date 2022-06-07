from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
import time, pymongo, os
from PIL import Image
import face_recognition


db_url = "mongodb+srv://Recognize:SPeDir6zC6wmUFwF@face.2cmws.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = pymongo.MongoClient(db_url)
db = "face-rec"
users_col = client[db]["users"]
event_col = client[db]["event_log"]

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/add/")
def add_user(request: Request):
    return templates.TemplateResponse("add.html", context={"request": request})


@app.post("/add/")
def add_user(
    request: Request,
    name: str = Form(...),
    surname: str = Form(...),
    formFile: UploadFile = File(...),
):
    image = Image.open(formFile.file)
    rgb_im = image.convert("RGB")
    rgb_im.save(name + "-" + surname + ".jpg")
    rgb_im = face_recognition.load_image_file(name + "-" + surname + ".jpg")
    face_encoding = face_recognition.face_encodings(rgb_im)[0]
    users_col.insert_one(
        {
            "name": name,
            "surname": surname,
            "face_encoding": face_encoding.tolist(),
            "enter_date": 0,
            "exit_date": 0,
            "first": 0,
            "flag": 0,
        }
    )
    if os.path.exists(name + "-" + surname + ".jpg"):
        os.remove(name + "-" + surname + ".jpg")

    result = name + " " + surname + "  successfully added."
    return templates.TemplateResponse(
        "add.html", context={"request": request, "sonuc": result}
    )


@app.get("/logs/")
def bulgu_ara(request: Request):
    sayfa = '<!DOCTYPE html><html lang="tr"> <head> <meta charset="UTF-8"> <meta http-equiv="X-UA-Compatible" content="IE=edge"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous"> <script type="text/javascript" src="https://code.jquery.com/jquery-3.5.1.js"></script> <link rel="stylesheet" href="https://cdn.datatables.net/1.11.4/css/jquery.dataTables.min.css"> <script src="https://cdn.datatables.net/1.11.4/js/jquery.dataTables.min.js"></script> </head> <body> <nav class="navbar navbar-expand-lg navbar-light bg-light"> <div class="container-fluid"> <a href="#" class="navbar-brand"> <b>TEDU PASS</b> </a> <button type="button" class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#navbarCollapse"> <span class="navbar-toggler-icon"></span> </button> <div class="collapse navbar-collapse" id="navbarCollapse"> <div class="navbar-nav"> <a href="/add/" class="nav-item nav-link active" >Add User</a> <a href="#" class="nav-item nav-link disabled" tabindex="-1">Logs</a></div></div></div></nav> <div class="container my-5 d-flex justify-content-center" id="content"> <div class="col-12"> <div class="card"> <div class="card-header">TEDU PASS Log Page</div><div class="card-body"> <table id="tableID" class="display"> <thead> <tr> <th>Date</th> <th>Name</th> <th>Action</th> </tr></thead> <tbody> <tr>'
    for x in event_col.find({}, {"_id": 0}).sort("ts", -1):
        sayfa = (
            sayfa
            + "<td>"
            + x["date"]
            + "</td> <td>"
            + x["name"]
            + "</td> <td>"
            + x["aksiyon"]
            + "</td> </tr>"
        )
    sayfa = (
        sayfa
        + "</tbody> </table> </div></div></div></div><script>$(document).ready(function(){$("
        + "'"
        + "#tableID"
        + "'"
        + ").DataTable("
        + "{"
        + "searching: true});});</script>"
        + '<footer class="text-center text-white fixed-bottom" style="background-color: #21081a;'
        + '"'
        + '> <div class="container p-1"></div><div class="text-center p-3" style="background-color: rgb(0, 0, 0);"> © 2022 - Dips </div></footer> </body></html>'
    )
    f = open("templates/bulgu-ara.html", "w")
    f.write(sayfa)
    f.close()
    return templates.TemplateResponse("bulgu-ara.html", context={"request": request})

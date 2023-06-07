from application import (
    app,
    valid_img_formats,
    valid_models,
    coarse_labels,
    columns_map,
    db,
)
from application.forms import LoginForm
from application.db_models import CifarPredictionEntry

from flask import render_template, flash, session, redirect, url_for, request
from flask_cors import CORS, cross_origin

import tensorflow.keras as keras

from PIL import Image
import numpy as np
import math
import json
import requests
import re
import base64
from datetime import datetime
from pathlib import Path

# parse canvas bytes and save as output.png
def parseImageData(imgData):
    base_path = "./application/static/images/uploads"
    now = datetime.now()
    str_now = now.strftime("%Y%m%d_%H%M%S")

    imgstr = re.search(b"base64,(.*)", imgData.encode()).group(1)
    with open(Path(f"{base_path}/upload_{str_now}.png"), "wb") as output:
        output.write(base64.decodebytes(imgstr))

    return base_path, f"upload_{str_now}.png"


def make_prediction(instances, target_url):
    data = json.dumps(
        {"signature_name": "serving_default", "instances": instances.tolist()}
    )
    headers = {"content-type": "application/json"}
    json_response = requests.post(target_url, data=data, headers=headers)
    predictions = json.loads(json_response.text)["predictions"]
    return predictions


def add_entry(new_entry):
    try:
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id
    except Exception as error:
        print(error)
        db.session.rollback()
        return False


def get_filepath_of_id(model, id):
    try:
        filepath = db.session.query(model.filepath).filter(model.id == id).all()[0][0]
        return filepath
    except Exception as error:
        print(error)
        db.session.rollback()
        return False


def get_number_of_entries(model):
    try:
        number = db.session.query(model).count()
        return number
    except Exception as error:
        print(error)
        db.session.rollback()
        return False


def get_entries(model, page, per_page, col, method):
    try:
        if method is None and col is None:
            q = db.session.query(model).paginate(page=page, per_page=per_page)
        else:
            if method == "desc":
                q = (
                    db.session.query(model)
                    .order_by(columns_map[col].desc())
                    .paginate(page=page, per_page=per_page)
                )
            elif method == "asc":
                q = (
                    db.session.query(model)
                    .order_by(columns_map[col].asc())
                    .paginate(page=page, per_page=per_page)
                )
        return q
    except Exception as error:
        print(error)
        db.session.rollback()
        return False


def delete_entry(model, id):
    try:
        model.query.filter_by(id=id).delete()
        db.session.commit()
        return True
    except Exception as error:
        print(error)
        db.session.rollback()
        return False


@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    if "username" not in session or session["username"] != app.config.get("USERNAME"):
        return redirect(url_for("login")), 307

    return render_template("index.html", loggedIn=True, title="Predict")


@app.route("/predict", methods=["POST"])
@cross_origin(origin="localhost", headers=["Content- Type", "Authorization"])
def predict():
    target_url = "https://bevanpoh-cifar-model.onrender.com"

    json_body = request.form
    image_data = json_body["image"]
    model = json_body["model"]
    filename = json_body["filename"]
    sharpen = float(json_body["edgeSharpen"])
    contrast = int(json_body["contrast"])

    file = Path(filename).stem
    extension = Path(filename).suffix
    if file is None or extension not in valid_img_formats:
        return {"status": "error", "message": "Invalid file"}, 422

    if (
        model not in valid_models
        or sharpen < 0.0
        or sharpen > 1.0
        or contrast < 0
        or contrast > 200
    ):
        return {"status": "error", "message": "Invalid input"}, 422

    try:
        saved_name = parseImageData(image_data)
    except Exception as error:
        print(error)
        return {"status": "error", "message": "Invalid image"}, 422

    img = keras.utils.img_to_array(keras.utils.load_img("/".join(saved_name)))
    img = img.reshape(1, 32, 32, 3)
    try:
        predictions = make_prediction(
            img, f"{target_url}/v1/models/{model}/versions/1:predict"
        )
        predicted_class = coarse_labels[np.argmax(predictions[0])]
    except:
        return {"status": "error", "message": "Model connection error"}, 500

    entry = CifarPredictionEntry(
        created_on=datetime.utcnow(),
        filename=filename,
        filepath=saved_name[1],
        prediction=predicted_class,
        model=model,
        contrast=contrast,
        sharpen=sharpen,
    )
    success = add_entry(entry)

    if not success:
        return {"status": "error", "message": "Database connection error"}, 500
    else:
        return {
            "status": "success",
            "message": predicted_class,
        }, 200


@app.route("/history", methods=["GET"])
def history():
    if "username" not in session or session["username"] != app.config.get("USERNAME"):
        return redirect(url_for("login")), 307

    per_page = 4
    maximum_page = math.ceil(get_number_of_entries(CifarPredictionEntry) / per_page)
    print(maximum_page)

    col = request.args.get("by")
    method = request.args.get("method")
    page = int(request.args.get("page", default=1))

    histories = get_entries(
        CifarPredictionEntry, page, per_page=per_page, col=col, method=method
    )
    print(page)
    if histories:
        return render_template(
            "history.html",
            loggedIn=True,
            current_page=page,
            current_method=method,
            current_column=col,
            maximum_page=maximum_page,
            histories=histories,
            columns=columns_map,
            title="History",
        ), 200
    else:
        flash("Error in retrieving records!", "danger!")
        return render_template(
            "history.html",
            loggedIn=True,
            current_page=1,
            maximum_page=maximum_page,
            columns=columns_map,
            title="History",
        ), 404


@app.route("/delete/<id>", methods=["GET"])
def delete(id):
    if "username" not in session or session["username"] != app.config.get("USERNAME"):
        return redirect(url_for("login")), 307

    filepath = get_filepath_of_id(CifarPredictionEntry, id)
    success = delete_entry(CifarPredictionEntry, id)
    print(filepath)
    if success:
        Path(f"./application/static/images/uploads/{filepath}").unlink(missing_ok=True)
        flash("Deleting entry was succesful", "success")
        return redirect(url_for("history")), 302
    else:
        flash("Deleting entry was unsuccesful! Please try again", "danger!")
        return redirect(url_for("history")), 307


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        form = LoginForm()
        if form.validate_on_submit():
            wrong_username = form.username.data != app.config.get("USERNAME")
            wrong_password = form.password.data != app.config.get("PASSWORD")
            if wrong_username or wrong_password:
                flash("Invalid username or password!")
                return (
                    render_template(
                        "login.html", form=LoginForm(), loggedin=False, title="Login"
                    ),
                    403,
                )

            session["username"] = form.username.data
            return redirect(url_for("index")), 302

    if request.method == "GET":
        if "username" not in session or session["username"] != app.config.get(
            "USERNAME"
        ):
            return (
                render_template(
                    "login.html", form=LoginForm(), loggedin=False, title="Login"
                ),
                200,
            )

        return redirect(url_for("index")), 302


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("username", None)
    return redirect(url_for("index")), 302

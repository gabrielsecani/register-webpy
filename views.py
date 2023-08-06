# -*- coding: UTF-8 -*-
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import desc, func
from models import Register, db
from app import app
from service import execute_job


@app.route("/")
def home():
    register_list = Register.query.order_by(Register.id.desc()).all()
    import json
    options = json.loads("""[
        {"id": "opt0", "value": "0", "label": "Opção 0"},
        {"id": "opt1", "value": "1", "label": "Opção 1"},
        {"id": "opt2", "value": "2", "label": "Opção 2"},
        {"id": "opt3", "value": "3", "label": "Opção 3"},
        {"id": "opt4", "value": "4", "label": "Opção 4"}
    ]""")
    
    return render_template("base.html", register_list=register_list, options=options)


@app.route("/add", methods=["POST"])
def add():
    # for debug
    print(request.form)
    print(request.files)
    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)
    wl_file_uploaded = request.files.get("file", None)
    wl_file_id = None
    if wl_file_uploaded:
        if wl_file_uploaded.filename == "":
            flash("No selected file")
            return redirect(request.url)
        from service import convertFileToDatabase

        wl_file_id = convertFileToDatabase(wl_file_uploaded)
        print("workload id: " + str(wl_file_id))
    name = request.form.get("name")
    company = request.form.get("company")
    options = "|".join(request.form.getlist("options"))
    new_register = Register(
        name=name, company=company, options=options, complete=False, workload=wl_file_id
    )
    print(db.session.add(new_register))
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/execute/<int:register_id>")
def execute(register_id):
    register = Register.query.filter_by(id=register_id).first()
    register.complete = False
    db.session.commit()
    execute_job(register.id)
    return redirect(url_for("home"))


@app.route("/delete/<int:register_id>")
def delete(register_id):
    register = Register.query.filter_by(id=register_id).first()
    print(register)
    db.session.delete(register)
    db.session.commit()
    return redirect(url_for("home"))


@app.errorhandler(404)
def not_found(error):
    return render_template("notfound.html", error=error)

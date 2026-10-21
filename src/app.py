import os
import sys
import pathlib

from flask import Flask, render_template, request, redirect, url_for
from platformdirs import user_data_dir
from datetime import datetime

import settings as Settings
from storage import Storage
from utils import str_to_date, count_hours, count_days

__APP__ = "Bunny"
__AUTHOR__ = "HugeBrain16"
__VERSION__ = "1.4.0"
__DIR__ = user_data_dir(__APP__, __AUTHOR__)
pathlib.Path(__DIR__).mkdir(parents=True, exist_ok=True)

DAYMAP = {
	"sunday": 0,
	"monday": 1,
	"tuesday": 2,
	"wednesday": 3,
	"thursday": 4,
	"friday": 5,
	"saturday": 6
}

DATAFILE = os.path.join(__DIR__, "bunny.db")
SETTINGSFILE = os.path.join(__DIR__, "settings.json")

def resource(path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.abspath("."), path)

# ==========================================================

template_dir = resource("templates")
static_dir = resource("static")

app = Flask(__APP__, template_folder=template_dir, static_folder=static_dir)
app.jinja_env.globals["today_date"] = lambda: datetime.now().astimezone()
app.jinja_env.filters['str_to_date'] = str_to_date

@app.route("/")
def route_index():
	db = Storage(DATAFILE)
	tasks = count_hours(db.serialize())
	tasks = count_days(tasks)

	settings = Settings.load(SETTINGSFILE)
	locales = sorted([f.stem for f in (pathlib.Path(app.static_folder) / "scripts" / "flatpickr-locales").iterdir() if f.is_file()])
	bunny = (pathlib.Path(app.static_folder) / "bunny.txt").open("r").read()

	return render_template("index.jinja2",
		tasks=tasks,
		settings=settings,
		locales=locales,
		bunny=bunny
	)

@app.route("/calendar", methods=["GET", "POST"])
def route_calendar():
	db = Storage(DATAFILE)
	tasks = count_hours(db.serialize())
	tasks = count_days(tasks)

	settings = Settings.load(SETTINGSFILE)

	if request.method == "POST":
		idx = int(request.form["index"])
		return render_template("calendar.jinja2", task=tasks[idx], taskIndex=idx, settings=settings)
	elif request.method == "GET":
		return render_template("calendar.jinja2", task=None, settings=settings)

@app.route("/delete", methods=["POST"])
def route_delete():
	db = Storage(DATAFILE)
	db.delete_task(int(request.form["index"]))
	db.write()

	return redirect(url_for("route_index"))

@app.route("/add", methods=["POST"])
def route_add():
	db = Storage(DATAFILE)

	if request.form["tStartDate"] == "" or request.form["tEndDate"] == "":
		return redirect(url_for("route_index"))

	try:
		db.add_task(
			request.form["tName"],
			request.form["tStartDate"],
			request.form["tEndDate"],
			int(request.form["tHours"]) + (int(request.form["tMinutes"]) / 60)
		)
		db.write()
	except ValueError:
		pass

	return redirect(url_for("route_index"))

@app.route("/edit", methods=["POST"])
def route_edit():
	db = Storage(DATAFILE)

	idx = int(request.form["tSubmit"])
	db.tasks[idx].name 		   = request.form["tName"]
	db.tasks[idx].start_date   = request.form["tStartDate"]
	db.tasks[idx].end_date 	   = request.form["tEndDate"]
	db.tasks[idx].target_hours = str(int(request.form["tHours"]) + (int(request.form["tMinutes"]) / 60))

	db.write()
	return redirect(url_for("route_index"))

@app.route("/unmark", methods=["POST"])
def route_unmark():
	db = Storage(DATAFILE)

	idx = int(request.form["tIndex"])
	date = request.form["tDate"]

	db.tasks[idx].remove_hours(date)
	db.write()

	tasks = count_hours(db.serialize())
	tasks = count_days(tasks)

	settings = Settings.load(SETTINGSFILE)

	return render_template("calendar.jinja2", task=tasks[idx], taskIndex=idx, settings=settings)

@app.route("/mark", methods=["POST"])
def route_mark():
	db = Storage(DATAFILE)

	ti = int(request.form["tIndex"])
	date = request.form["tDate"]
	hours = int(request.form["tHours"])
	minutes = int(request.form["tMinutes"]) / 60
	color = request.form["tColor"]
	note = request.form["tNote"]

	db.tasks[ti].add_hours(date, hours + minutes)

	for hi, h in enumerate(db.tasks[ti]._hours):
		if h.date == date:
			db.tasks[ti]._hours[hi].set_color(color)
			db.tasks[ti]._hours[hi].set_note(note)

	db.write()

	tasks = count_hours(db.serialize())
	tasks = count_days(tasks)

	settings = Settings.load(SETTINGSFILE)

	return render_template("calendar.jinja2", task=tasks[ti], taskIndex=ti, settings=settings)

@app.route("/settings", methods=["POST"])
def route_settings():
	settings = Settings.load(SETTINGSFILE)

	settings["locale"] 		= request.form["tLocale"]
	settings["first_day"] 	= DAYMAP[request.form["tFirstDay"]]
	settings["red_sundays"] = request.form.get("tRedSundays") == "yes"
	settings["week_total"]  = request.form.get("tWeekTotal") == "yes"

	Settings.write(SETTINGSFILE, settings)

	return redirect(url_for("route_index"))

# ==========================================================

if __name__ == "__main__":
	app.run(host="127.0.0.1", port=5000, debug=True)

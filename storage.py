import os
import json

class Hours:
	def __init__(self, date, hours):
		self.date = date
		self.hours = hours

		self._note = None

	def add_note(self, text):
		self._note = text

	def get_note(self):
		return self._note

class Task:
	def __init__(self, name, start_date, end_date, target_hours):
		self.name = name
		self.start_date = start_date
		self.end_date = end_date
		self.target_hours = target_hours

		self._hours = []

	def add_hours(self, date, hours):
		for i, h in enumerate(self._hours):
			if h.date == date:
				self._hours[i].hours = hours
				return

		self._hours.append(Hours(date, hours));

	def remove_hours(self, date):
		for i, h in enumerate(self._hours):
			if h.date == date:
				del self._hours[i]
				return

	def total_hours(self):
		hours = 0

		for h in self._hours:
			hours += h.hours

		return hours

class Storage:
	def __init__(self, file):
		self.file = file
		self.tasks = []

		if not os.path.isfile(file) or len(open(file, "r").read().strip()) == 0:
			with open(file, "w") as f:
				f.write("{}")

		with open(file, "r") as f:
			data = json.loads(f.read())

			for t in data.values():
				task = self.add_task(t["name"], t["start_date"], t["end_date"], t["target_hours"])

				for h in t["hours"].values():
					hours = Hours(h["date"], h["hours"])
					if h["note"]:
						hours.add_note(h["note"])

					task._hours.append(hours)

	def write(self):
		with open(self.file, "w") as f:
			f.write(json.dumps(self.serialize(), indent=2))

	def serialize(self):
		data = {}

		for ti, t in enumerate(self.tasks):
			task = {
				"name": t.name,
				"start_date": t.start_date,
				"end_date": t.end_date,
				"target_hours": t.target_hours,
				"hours": {}
			}

			for hi, h in enumerate(t._hours):
				task["hours"][hi] = {
					"date": h.date,
					"hours": h.hours,
					"note": h.get_note()
				}

			data[ti] = task

		return data

	def add_task(self, name, start_date, end_date, target_hours):
		task = Task(name, start_date, end_date, target_hours)
		self.tasks.append(task)

		return task

	def delete_task(self, index):
		del self.tasks[index]

	def find_task_by_name(self, name):
		for task in self.tasks:
			if task.name == name:
				return task

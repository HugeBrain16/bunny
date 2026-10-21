from datetime import datetime

def str_to_date(value, fmt="%Y-%m-%d"):
    return datetime.strptime(value, fmt).astimezone()

def valid_date(datestr):
	try:
		str_to_date(datestr)
		return True
	except ValueError:
		return False

def count_hours(tasks):
	for task in tasks.values():
		total = 0
		for hours in task["hours"].values():
			total += hours["hours"]
		task["total_hours"] = total

	return tasks

def count_days(tasks):
	for task in tasks.values():
		strftime = "%Y-%m-%d"

		start = datetime.strptime(task["start_date"], strftime);
		end = datetime.strptime(task["end_date"], strftime);

		task["total_days"] = (end - start).days

	return tasks
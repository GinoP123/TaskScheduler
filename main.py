#!/usr/bin/env python3

import csv
import settings
import random
import sys
import subprocess as sp
import datetime
import os
import encrypt


def get_tasks():
	with open(settings.tasks_path) as tasks_file:
		tasks = list(csv.reader(tasks_file))
	return tasks


def update_tasks(tasks):
	with open(settings.tasks_path, 'w') as tasks_file:
		csv.writer(tasks_file).writerows(tasks)


def get_sum(tasks):
	if os.path.getmtime(settings.sum_path) < os.path.getmtime(settings.tasks_path):
		update_sum(sum(map(lambda x: int(x[1]), tasks)))
	with open(settings.sum_path) as infile:
		return int(infile.read().strip())


def update_sum(new_sum):
	with open(settings.sum_path, 'w') as outfile:
		outfile.write(str(new_sum))


def update_gravy(task):
	with open(settings.gravy_path, 'a') as outfile:
		outfile.write(f"{task}\n")


def decrement_task(tasks, index):
	task = tasks[index]
	if task[1] == '1':
		update_gravy(tasks.pop(index)[0])
	else:
		task[1] = str(int(task[1]) - 1)
	update_tasks(tasks)
	return task[0]


def get_new_task_info():
	name = ""
	units = ""

	print()
	while not name:
		name = input(settings.input_name)
	while not units.isnumeric():
		units = input(settings.input_units)
	print("\n")

	return name, int(units)


def add_task():
	name, units = get_new_task_info()
	tasks = get_tasks()
	tasks.append([name, str(units)])
	update_tasks(tasks)
	update_sum(get_sum(tasks) + units)


def list_tasks():
	tasks = get_tasks()

	if not tasks:
		print(settings.no_task_message)
		exit()

	print(settings.task_column_labels)
	for task in tasks:
		print(settings.task_string.format(task[0]))


def pick_task():
	tasks = get_tasks()
	tasks_sum = get_sum(tasks)
	task = random.randint(1, tasks_sum)

	picked_task = -1
	while task > 0:
		picked_task += 1
		task -= int(tasks[picked_task][1])
	task = decrement_task(tasks, picked_task)
	update_sum(tasks_sum - 1)
	return task


def check_time():
	with open(settings.time_file) as infile:
		time = encrypt.decrypt(infile.read())
	time = datetime.datetime.strptime(time, settings.time_format)
	diff = (datetime.datetime.now() - time).seconds // 60
	return diff >= int(settings.time_designated)


def set_time():
	with open(settings.time_file, 'w') as outfile:
		time = datetime.datetime.now().strftime(settings.time_format)
		outfile.write(encrypt.encrypt(time))


def main():
	if check_time():
		task = pick_task()
		if task:
			sp.run([settings.alarm_setter_path, "set", 
				settings.time_until_break, 
				settings.break_message.format(task)])
			sp.run([settings.alarm_setter_path, "set", 
				settings.time_designated, 
				settings.break_over_message])
			print(settings.next_task_message.format(task))
			set_time()
		else:
			print(settings.no_task_message)
	else:
		print(settings.keep_working_message)



if __name__ == "__main__":
	assert len(sys.argv)
	os.chdir(os.path.dirname(sys.argv[0]))

	command = ''.join(sys.argv[1:])
	if command == "next":
		main()
	elif command == "add":
		add_task()
	elif command == "list":
		list_tasks()
	else:
		raise AssertionError(settings.invalid_syntax_message)


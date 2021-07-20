import os
import telebot
from telebot import types
import sqlite3

channel_id = '-1001561042541'

con = sqlite3.connect('tutors.db')
db = con.cursor()

# db.execute("CREATE TABLE IF NOT EXISTS tutor_list (id INTEGER PRIMARY KEY, username TEXT NOT NULL, gender TEXT, occupation TEXT, available TEXT, other TEXT)")

# db.execute("CREATE TABLE subjects (id INTEGER, tutor_id INTEGER, subject TEXT, PRIMARY KEY (id), FOREIGN KEY (tutor_id) REFERENCES tutor_list(id))")

# db.execute("CREATE TABLE levels (id INTEGER, tutor_id INTEGER, level TEXT, PRIMARY KEY (id), FOREIGN KEY (tutor_id) REFERENCES tutor_list(id))")

API_KEY = os.environ['API_KEY']

bot = telebot.TeleBot(API_KEY)

parent_pref = {}

@bot.message_handler(commands=['hello'])
def hello(message):
	markup = types.ReplyKeyboardMarkup(row_width=1)
	itembtn1 = types.KeyboardButton('Looking for a tutor')
	itembtn2 = types.KeyboardButton('A tutor')
	itembtn3 = types.KeyboardButton('Looking to contact admin')
	markup.add(itembtn1, itembtn2, itembtn3)
	bot.send_message(message.chat.id, "Hello! Welcome to the best Tutor Finder bot. Are you:", reply_markup=markup)

@bot.message_handler(regexp='Looking to contact admin')
def reply_parent(message):
	msg = bot.send_message(message.chat.id, "Please type here what you want to send to admin!")
	bot.register_next_step_handler(msg, admin_help)

def admin_help(message):
	helptext = message.text
	username = message.from_user.username
	bot.send_message(chat_id = '306867255', text=f'From https://t.me/{username} : {helptext}')

@bot.message_handler(regexp='Looking for a tutor')
def reply_parent(message):
	markup = types.ReplyKeyboardMarkup(row_width=1)
	itembtn1 = types.KeyboardButton('Primary')
	itembtn2 = types.KeyboardButton('Secondary')
	itembtn3 = types.KeyboardButton('JC')
	markup.add(itembtn1, itembtn2, itembtn3)
	msg = bot.send_message(message.chat.id, "What level do you want your tutor to teach? Kindly submit one request form per level.", reply_markup=markup)
	bot.register_next_step_handler(msg, set_subjects_parent)

def set_subjects_parent(message):
	level = message.text
	parent_pref["level"] = level
	msg = bot.send_message(message.chat.id, "What subject do you want your tutor to teach? Kindly submit one request form per level.")
	bot.register_next_step_handler(msg, set_occupation_parent)

def set_occupation_parent(message):
	subject = message.text
	parent_pref["subject"] = subject
	markup = types.ReplyKeyboardMarkup(row_width=1)
	itembtn1 = types.KeyboardButton('Current Student')
	itembtn2 = types.KeyboardButton('Waiting to Begin School')
	itembtn3 = types.KeyboardButton('Employed/Full-Time Tutor')
	markup.add(itembtn1, itembtn2, itembtn3)
	msg = bot.send_message(message.chat.id, "What stage of life do you want your tutor to be in?", reply_markup=markup)
	bot.register_next_step_handler(msg, submit_occupation_request)


def submit_occupation_request(message):
	occupation = message.text
	parent_pref["occupation"] = occupation
	msg = bot.send_message(message.chat.id, "Finding you a match... Type anything to see your match.")
	bot.register_next_step_handler(msg, submit_parent_request)


def submit_parent_request(message):
	con = sqlite3.connect('tutors.db')
	db = con.cursor()
	subject = parent_pref["subject"]
	level = parent_pref["level"]
	occupation = parent_pref["occupation"]
	tutors = []
	db.execute("SELECT tutor_list.username FROM tutor_list JOIN subjects ON subjects.tutor_id = tutor_list.id JOIN levels ON levels.tutor_id = tutor_list.id WHERE subjects.subject = ? AND levels.level = ? AND tutor_list.occupation = ?", [subject, level, occupation])
	tutors = db.fetchall()
	i = 0
	if not tutors:
		bot.send_message(message.chat.id, text="Unfortunately, we couldn't find a perfect match for you. Try changing your preferences a bit. Support for near-matches will be implemented soon.")
	else:
		for tutor in tutors:
			tutor = str(tutor)
			tutor = tutor.replace("(", "").replace(")", "").replace("'", "").replace(",", "")
			i += 1
			con = sqlite3.connect('tutors.db')
			db = con.cursor()
			db.execute("SELECT tutor_list.gender FROM tutor_list WHERE username=?", [tutor])
			gender = db.fetchall()
			gender = gender[0]
			gender = str(gender)
			gender = gender.replace("'", "").replace("(", "").replace(")", "").replace(",", "")
			bot.send_message(message.chat.id, parse_mode='HTML', text='Tutor {}: <a href="https://t.me/{}">Contact <b>Here</b></a>. \nTeaches <b>{}</b> at <b>{}</b> level. \n<b>Gender</b>: {}. \n<b>Occupation</b>: {}'.format(i, tutor, subject, level, gender, occupation))

@bot.message_handler(regexp='A tutor')
def reply_tutor(message):
	user_id = message.from_user.id
	user_id = str(user_id)
	con = sqlite3.connect('tutors.db')
	db = con.cursor()
	db.execute("SELECT id FROM tutor_list")
	ids = db.fetchall()
	for id in ids:
		id = str(id)
		id = id.replace("(", "").replace(")", "").replace("'", "").replace(",","")
		# If tutor has signed up before, give options to edit profile or delete profile. 
		if user_id == id:
			markup = types.ReplyKeyboardMarkup(row_width=1)
			itembtn1 = types.KeyboardButton('Edit Profile')
			itembtn2 = types.KeyboardButton('Toggle Availability')
			itembtn3 = types.KeyboardButton('Delete Profile')
			markup.add(itembtn1, itembtn2, itembtn3)
			msg = bot.send_message(message.chat.id, "You signed up before. What do you want to do?", reply_markup=markup)
			bot.register_next_step_handler(msg, registered_choices)
			return
	msg = bot.send_message(message.chat.id, "What is your Telegram username? Don't put @.")
	bot.register_next_step_handler(msg, set_username)

def registered_choices(message):
	messagetxt = message.text
	user_id = message.from_user.id
	if messagetxt == 'Edit Profile':
		pass
	elif messagetxt == 'Toggle Availability':
		con = sqlite3.connect('tutors.db')
		db = con.cursor()
		db.execute("SELECT available FROM tutor_list WHERE id = ?", [user_id])
		availability = db.fetchall()
		availability = availability[0]
		availability = str(occupation)
		availability = availability.replace("'", "").replace("(", "").replace(")", "").replace(",", "")
		if availability == 'Yes':
			con = sqlite3.connect('tutors.db')
			db = con.cursor()
			db.execute("UPDATE tutors_list SET availability = 'No' WHERE id = ?", user_id)
			bot.send_message("Availability toggled to No. If your post isn't deleted off the channel, contact admin.")
			# Add support to delete their post off the channel.
		else:
			con = sqlite3.connect('tutors.db')
			db = con.cursor()
			db.execute("UPDATE tutors_list SET availability = 'Yes' WHERE id = ?", [user_id])
			bot.send_message("Availability toggled to Yes. If your post isn't deleted off the channel, contact admin.")
			# Add support to post it on the channel

	elif messagetxt == 'Delete Profile':
		con = sqlite3.connect('tutors.db')
		db = con.cursor()
		db.execute("DELETE FROM tutor_list WHERE id = ?", [user_id])
		con.commit()
		db.execute("DELETE FROM subjects WHERE tutor_id = ?", [user_id])
		con.commit()
		db.execute("DELETE FROM levels WHERE tutor_id = ?", [user_id])
		con.commit()
		bot.send_message(message.chat.id, "Deleted!")
		return

def set_username(message):
	usernamenow = message.text
	user_id = message.from_user.id
	# See if user_id exists already
	con = sqlite3.connect('tutors.db')
	db = con.cursor()
	db.execute("INSERT INTO tutor_list (username, id) VALUES (?, ?)", [usernamenow, user_id])
	con.commit()
	msg = bot.send_message(message.chat.id, "What subjects do you teach? Please separate each subject with a comma and a space.")
	bot.register_next_step_handler(msg, set_subjects_tutor)
# Figure out a way to store the reply into the database 

def set_subjects_tutor(message):
	user_id = message.from_user.id
	subjects = []
	subjects = message.text.split(", ")
	for subject in subjects:
		con = sqlite3.connect('tutors.db')
		db = con.cursor()
		db.execute("INSERT INTO subjects (subject, tutor_id) VALUES (?, ?)", [subject, user_id])
		con.commit()
	msg = bot.send_message(message.chat.id, "What levels do you teach? Options: Primary/Secondary/JC. Please separate each level with a comma and a space.")
	bot.register_next_step_handler(msg, set_level_tutor)

#ADD SUBJECT
def set_level_tutor(message):
	user_id = message.from_user.id
	levels = []
	levels = message.text.split(", ")
	for level in levels:
		con = sqlite3.connect('tutors.db')
		db = con.cursor()
		db.execute("INSERT INTO levels (level, tutor_id) VALUES (?, ?)", [level, user_id])
		con.commit()
	markup = types.ReplyKeyboardMarkup(row_width=1)
	itembtn1 = types.KeyboardButton('Female')
	itembtn2 = types.KeyboardButton('Male')
	itembtn3 = types.KeyboardButton('Non-Binary')
	# itembtn4 = types.KeyBoardButton('Prefer Not To Say')
	markup.add(itembtn1, itembtn2, itembtn3)
	msg = bot.send_message(message.chat.id, "What is your gender identity? Parents will not be able to filter by gender, but it will be shown on your profile.", reply_markup=markup)
	bot.register_next_step_handler(msg, set_gender_tutor)

def set_gender_tutor(message):
	user_id = message.from_user.id
	gender = message.text
	con = sqlite3.connect('tutors.db')
	db = con.cursor()
	db.execute("UPDATE tutor_list SET gender = ? WHERE id = ?", [gender, user_id])
	con.commit()
	markup = types.ReplyKeyboardMarkup(row_width=1)
	itembtn1 = types.KeyboardButton('Current Student')
	itembtn2 = types.KeyboardButton('Waiting to Begin School')
	itembtn3 = types.KeyboardButton('Employed/Full-Time Tutor')
	markup.add(itembtn1, itembtn2, itembtn3)
	msg = bot.send_message(message.chat.id, "What stage of life are you currently in? Note NS etc falls under Waiting to Begin School.", reply_markup=markup)
	bot.register_next_step_handler(msg, set_occupation_tutor)

def set_occupation_tutor(message):
	user_id = message.from_user.id
	occupation = message.text
	con = sqlite3.connect('tutors.db')
	db = con.cursor()
	db.execute("UPDATE tutor_list SET occupation = ? WHERE id = ?", [occupation, user_id])
	con.commit()
	msg = bot.send_message(message.chat.id, "If there is any additional information you want to provide, please do so now. E.G. Grades in relevant subjects, School, Teaching Style, etc. Only do so if you are comfortable with having your information posted on the channel. Privacy is important!")
	bot.register_next_step_handler(msg, set_other_tutor)

def set_other_tutor(message):
	user_id = message.from_user.id
	other = message.text
	con = sqlite3.connect('tutors.db')
	db = con.cursor()
	db.execute("UPDATE tutor_list SET other = ? WHERE id = ?", [other, user_id])
	con.commit()
	markup = types.ReplyKeyboardMarkup(row_width=1)
	itembtn1 = types.KeyboardButton('Yes')
	itembtn2 = types.KeyboardButton('No')
	markup.add(itembtn1, itembtn2)
	msg = bot.send_message(message.chat.id, "Indicate if you are looking for tuition jobs now and parents can contact you to ask about that. You can change your availability at anytime, but it won't do much for now. If No, we will store your info in our database for future reference but we won't post you up on the channel.", reply_markup=markup) # Update when finished
	bot.register_next_step_handler(msg, set_availability)

def set_availability(message):
	user_id = message.from_user.id
	availability = message.text
	con = sqlite3.connect('tutors.db')
	db = con.cursor()
	db.execute("UPDATE tutor_list SET available = ? WHERE id = ?", [availability, user_id])
	con.commit()
	if availability == 'Yes':
		markup = types.ReplyKeyboardMarkup(row_width=1)
		itembtn1 = types.KeyboardButton('Yes')
		itembtn2 = types.KeyboardButton('No')
		markup.add(itembtn1, itembtn2)
		msg = bot.send_message(message.chat.id, "Great! Are you willing to have this info published on the channel? If No, your application will be deleted. Note that your Tele Username will be posted on the channel for parents to contact until the developer figures out an alternative, so please strengthen your privacy settings. You can decide to take down your post anytime later, just contact admin.", reply_markup=markup)
		bot.register_next_step_handler(msg, set_willingness)
	elif availability == 'No':
		bot.send_message(message.chat.id, "Your information will be stored in our database, but we won't post it on the channel. Goodbye and thanks for using Tutor Finder Bot!")

def set_willingness(message):
	answer = message.text
	if answer == 'Yes':
		msg = bot.send_message(message.chat.id, "Awesome! Type any message and your post will be posted up on the channel. Goodbye and thank you for using Tutor Finder Bot!")	
		# Test: send to channel
		bot.register_next_step_handler(msg, broadcast)
		# Post to telegram channel
	elif answer == 'No':
		bot.send_message(message.chat.id, "Sorry to see you go. Your application is deleted!")
		user_id = message.from_user.id
		con = sqlite3.connect('tutors.db')
		db = con.cursor()
		db.execute("DELETE FROM tutor_list WHERE id = ?", user_id)
		con.commit()

def broadcast(message):
	user_id = message.from_user.id
	con = sqlite3.connect('tutors.db')
	db = con.cursor()
	db.execute("SELECT username FROM tutor_list WHERE id = ?", [user_id])
	username = db.fetchall()
	username = username[0]
	username = str(username)
	username = username.replace("'", "").replace("(", "").replace(")", "").replace(",", "")
	db.execute("SELECT other FROM tutor_list WHERE id = ?", [user_id])
	other = db.fetchall()
	other = other[0]
	other = str(other)
	other = other.replace("'", "").replace("(", "").replace(")", "").replace(",", "")
	db.execute("SELECT gender FROM tutor_list WHERE id = ?", [user_id])
	gender = db.fetchall()
	gender = gender[0]
	gender = str(gender)
	gender = gender.replace("'", "").replace("(", "").replace(")", "").replace(",", "")
	db.execute("SELECT occupation FROM tutor_list WHERE id = ?", [user_id])
	occupation = db.fetchall()
	occupation = occupation[0]
	occupation = str(occupation)
	occupation = occupation.replace("'", "").replace("(", "").replace(")", "").replace(",", "")
	db.execute("SELECT level FROM levels WHERE tutor_id = ?", [user_id])
	levels = db.fetchall()
	levels_new = ''
	# Make it look correct
	for level in levels:
		level = str(level)
		level = level.replace("(", "").replace(")", "").replace("'", "")
		levels_new += level
	n = len(levels_new)
	levels_new = levels_new[0:n-1]
	levels_new = levels_new.replace(",", ", ")
	db.execute("SELECT subject FROM subjects WHERE tutor_id = ?", [user_id])
	subjects = db.fetchall()
	subjects_new = ''
	for subject in subjects:
		subject = str(subject)
		subject = subject.replace("(", "").replace(")", "").replace("'", "")
		subjects_new += subject
	n = len(subjects_new)
	subjects_new = subjects_new[0:n-1]
	subjects_new = subjects_new.replace(",", ", ")

	# Contact User
	# Send msg
	# markup = types.ReplyKeyboardMarkup(row_width=1)
	# itembtn1 = types.KeyboardButton('Request to Contact Tutor')
	# markup.add(itembtn1)
	bot.send_message(chat_id='-1001561042541', text=f"New Tutor!\nSubjects: {subjects_new} \nLevels: {levels_new}\nGender: {gender} \nStage In Life: {occupation} \nNotes: {other}")
	bot.send_message(chat_id='-1001561042541', parse_mode='HTML', text='Contact User <a href="https://t.me/{}">Here</a>'.format(username))
	# Attempt at privacy protection. I need to figure out how to get a button to register interest without sending a msg.
	# bot.send_message()

bot.enable_save_next_step_handlers(delay=2)

bot.load_next_step_handlers()

bot.polling()

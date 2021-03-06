import MySQLdb.cursors
import hashlib
from random import randrange
from datetime import datetime, timedelta

unit_names = ["Cat Care Specialists", "IT Infrastructure Group",
	"Grouper Group", "Tuna Group", "Salmon Group", "Stray Pig News",
	"Some People", "Some Other People", "Pretty Okay People",
	"People Who Do Stuff", "Nothing To See Here"]

people_names = ["George", "Fred", "Harry", "Hermione", "Tammy", "Imogen",
	"William", "Alexander", "David", "David", "David", "David", "Marisa",
	"Marissa", "Alice", "Sarah", "Max", "Chloe", "Warren"]

# QUERIES FOR GETTING INFORMATION ABOUT MODULES
def get_module_info():
    """ get basic information about modules """
    modules = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT MODULE_ID, NAME, BLURB, NUM_SLIDES + NUM_QUIZ_QUESTIONS + NUM_INT_QUESTIONS AS TOTAL_SLIDES FROM MODULES WHERE status = 'ACTIVE'")
    rows = cur.fetchall()
    for row in rows:
	modules.append(row)
    conn.close()
    return modules

def get_module_id_from_name(module_name):
    """ get id from module name """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT MODULE_ID FROM MODULES WHERE NAME = %s", [module_name])
    row = cur.fetchone()
    conn.close()
    return row['MODULE_ID']

def get_module_names():
    """ get list of module names to check against"""
    modules = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT NAME FROM MODULES WHERE status = 'ACTIVE'")
    rows = cur.fetchall()
    for row in rows:
	modules.append(row['NAME'].lower())
    conn.close()
    return modules

def get_all_module_names():
    """ get list of module names to check against"""
    modules = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT NAME FROM MODULES")
    rows = cur.fetchall()
    for row in rows:
	modules.append(row['NAME'].lower())
    conn.close()
    return modules

def get_all_module_names():
    """ get list of module names to check against"""
    modules = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT NAME FROM MODULES")
    rows = cur.fetchall()
    for row in rows:
	modules.append(row['NAME'].lower())
    conn.close()
    return modules

def get_admin_module_info():
    """ get module information for administrators """
    modules = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM vw_ADMIN_MODULE_INFO ORDER BY STATUS ASC, MODULE_ID ASC")
    rows = cur.fetchall()
    for row in rows:
	row['LAST_UPDATED'] = row['LAST_UPDATED'].strftime('%d-%m-%Y')
	modules.append(row)
    conn.close()
    return modules

def get_module_edit_info(id):
    """ get module name and blurb to display in profile edit module """

    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT NAME, BLURB FROM vw_ADMIN_MODULE_INFO WHERE MODULE_ID = %s", [id]);
    info = cur.fetchone()
    return info

def get_num_q(id):
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT NUM_QUIZ_QUESTIONS, NUM_INT_QUESTIONS FROM MODULES WHERE MODULE_ID = %s", [id]);
    info = cur.fetchone()
    return [info['NUM_QUIZ_QUESTIONS'], info['NUM_INT_QUESTIONS']]

def add_new_module_profile(name, blurb):
    """ add the new module name and blurb created by the administrator to the database"""
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO MODULES (NAME, STATUS, BLURB) VALUES (%s, %s, %s)", 
	    [name, 'INACTIVE', blurb])
    conn.commit()
    new_module_id = cur.lastrowid
    conn.close()
    return new_module_id

def add_new_revision(mid, revision, content, user):
    """ add a new revision of a newly modified module to the database """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO MODULE_CONTENT (MODULE_ID, REVISION, CONTENT, EDITOR) VALUES (%s, %s, %s, %s)", 
	    [mid, revision + 1, content, user])
    conn.commit()

def edit_last_revision(mid, revision, content, user):
    """ edit the last revision of a modified module in the database """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("UPDATE MODULE_CONTENT SET CONTENT = %s, EDITOR = %s, TIME_CREATED = NOW() WHERE MODULE_ID = %s AND REVISION = %s", 
	    [content, user, mid, revision])
    conn.commit()

def update_module_content(mid, content, user):
    """ update the slide content of a module in the database """
    info = get_latest_revision(mid)
    update_time = info['TIME_CREATED']
    curr_time = datetime.now() 
    if ((curr_time - update_time) < timedelta(minutes = 15)):
	edit_last_revision(mid, info['REVISION'], content, user)
    else:
	add_new_revision(mid, info['REVISION'], content, user)

def get_latest_revision(mid):
    """ get the latest revised version of a module from the database """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT REVISION, TIME_CREATED FROM MODULE_CONTENT WHERE MODULE_ID = %s ORDER BY REVISION DESC", 
	    [mid])
    row = cur.fetchone()
    conn.close()
    return row

def edit_module_profile(mid, name, blurb):
    """ update the name and blurb of a module in the database """
    conn = do_mysql_connect()
    cur = conn.cursor()
    try:
	cur.execute("UPDATE MODULES SET NAME = %s, BLURB = %s WHERE MODULE_ID = %s", 
		[name, blurb, mid])
	conn.commit()
	return 0
    except MySQLdb.Error as e:
	conn.rollback()
    return e
    conn.close()

def get_module_status(mid):
    """ get the status of a module from the database; i.e active or inactive """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT STATUS FROM MODULES WHERE MODULE_ID = %s", [mid])
    row = cur.fetchone()
    conn.close()
    return row['STATUS']

def toggle_module_status(mid):
    """ update the status of a module in the database """
    conn = do_mysql_connect()
    cur = conn.cursor()
    status = get_module_status(mid)
    q_num = get_num_q(mid)
    if status == 'ACTIVE':
	cur.execute("UPDATE MODULES SET STATUS = %s WHERE MODULE_ID = %s", ["INACTIVE", mid])
	conn.commit()
	return 1
    else:
	if (q_num[0] >= 1 and q_num[1] >= 1):
	    cur.execute("UPDATE MODULES SET STATUS = %s WHERE MODULE_ID = %s", ["ACTIVE", mid])
	    conn.commit()
	    return 0
	else:
	    return -1
    conn.close()

def get_last_updated_module():
    """ get last updated module information for administrators """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM vw_ADMIN_MODULE_INFO ORDER BY LAST_UPDATED DESC LIMIT 1")
    module = cur.fetchone()
    return module

def get_module_content(module_id):
    """ gets latest revision of module content """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT CONTENT FROM MODULE_CONTENT WHERE MODULE_ID = %s ORDER BY REVISION DESC", [module_id])
    row = cur.fetchone()
    return row['CONTENT']

def get_quiz_questions_by_module(module_id):
    """ get list of questions per module """
    questions = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM QUIZ_QUESTIONS WHERE MODULE_ID = %s", [module_id])
    rows = cur.fetchall()
    for row in rows:
	questions.append(row)
    conn.close()
    return questions

def get_question_statistics():
    """ get question statistics """
    stats = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT QUESTION_ID, PERCENT_SUCCESS FROM vw_QUESTION_STATISTICS")
    rows = cur.fetchall()
    for row in rows:
	stats.append(row)
    conn.close()
    return stats

def get_questions_answered_by_user(uid):
    """ get number of questions answered by user """
    number_of_answers = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(QUESTION_ID) AS QUESTIONS_ANSWERED FROM GRADEBOOK WHERE USER_ID = %s AND QUESTION_TYPE = %s", [uid, "QUIZ"])
    rows = cur.fetchall()
    for row in rows:
        number_of_answers.append(row['QUESTIONS_ANSWERED'])
    conn.close()
    return number_of_answers

def get_correct_answers():
    """ get list of correct answers """
    answers = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM QUIZ_CORRECT")
    rows = cur.fetchall()
    for row in rows:
	answers.append(row['ANSWER_ID'])
    conn.close()
    return answers

def get_quiz_answers_by_user(uid):
    """ get list of answers by user id """
    answers = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM GRADEBOOK WHERE USER_ID = %s AND QUESTION_TYPE = %s", [uid, "QUIZ"])
    rows = cur.fetchall()
    for row in rows:
	answers.append(row['ANSWER_ID'])
    conn.close()
    return answers

def modules_completed_by_user(user_id):
    """ get list of modules that the user has already completed """
    modules_completed = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT A.MODULE_ID FROM MODULES M,(SELECT MODULE_ID,COUNT(MODULE_ID) AS COUNT FROM vw_USER_QUIZ_ANSWERS WHERE USER_ID = %s GROUP BY MODULE_ID) AS A WHERE COUNT = M.NUM_QUIZ_QUESTIONS", [user_id])
    rows = cur.fetchall()
    for row in rows:
	modules_completed.append(row['MODULE_ID'])
    conn.close()
    return modules_completed

def get_modules_started_by_user(user_id):
    """ get list of modules started by the user; module could be completed or not"""
    modules_started = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT MODULE_ID FROM USER_PROGRESS WHERE USER_ID=%s", [user_id])
    rows = cur.fetchall()
    for row in rows:
	modules_started.append(row['MODULE_ID'])
    conn.close()
    return modules_started

def get_last_viewed_slide_by_user(user_id):
    """ get the last viewed slide for modules in progress by user """
    last_viewed_slides = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT MODULE_ID, LAST_VIEWED FROM USER_PROGRESS WHERE USER_ID=%s", [user_id])
    rows = cur.fetchall()
    for row in rows:
	last_viewed_slides.append(row)
    conn.close()
    return last_viewed_slides

def get_quiz_questions_by_module(module_id):
    """ get list of questions per module """
    quiz_questions_by_module = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM QUIZ_QUESTIONS WHERE MODULE_ID = %s", [module_id])
    rows = cur.fetchall()
    for row in rows:
	quiz_questions_by_module.append(row)
    conn.close()
    return quiz_questions_by_module
    
def get_quiz_answers():
    """ get list of all quiz answers to quiz questions"""
    quiz_answers = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    # modify this to only get answers for one module's questions
    cur.execute("SELECT * FROM QUIZ_ANSWERS")
    rows = cur.fetchall()
    for row in rows:
	quiz_answers.append(row)
    conn.close()
    return quiz_answers

def get_int_questions_by_module(module_id):
    """ get list of interactive questions per module """
    int_questions_by_module = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM INTERACTIVE_QUESTIONS WHERE MODULE_ID = %s", [module_id])
    rows = cur.fetchall()
    for row in rows:
	int_questions_by_module.append(row)
    conn.close()
    return int_questions_by_module
    
def get_int_answers():
    """ get list of all answers to interactive questions"""
    int_answers = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    # modify this to only get answers for one module's questions
    cur.execute("SELECT * FROM INTERACTIVE_ANSWERS")
    rows = cur.fetchall()
    for row in rows:
	int_answers.append(row)
    conn.close()
    return int_answers

def get_int_correct_answers():
    """ get list of all correct answers to interactive questions"""
    correct_answers = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    # modify this to only get answers for one module's questions
    cur.execute("SELECT * FROM INTERACTIVE_CORRECT")
    rows = cur.fetchall()
    for row in rows:
	correct_answers.append(row['INT_ANS_ID'])
    conn.close()
    return correct_answers

def get_number_of_correct_answers(user_id, module_title):
    """ get number of correct answer by module for each user """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(QUESTION_ID) AS QUESTIONS_CORRECT FROM vw_USER_QUIZ_CORRECT WHERE USER_ID = %s AND MODULE_ID IN (SELECT MODULE_ID FROM MODULES WHERE NAME = %s) GROUP BY USER_ID, MODULE_ID", [user_id, module_title])
    rows = cur.fetchall()
    
    if (rows):
	for row in rows:
	    correct_answers = row['QUESTIONS_CORRECT']
    else:
        correct_answers = 0
    
    conn.close()
    return correct_answers

def get_total_number_of_questions(module_title):
    """ get the total number of questions per module """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("Select MODULE_ID, NUM_QUIZ_QUESTIONS FROM MODULES WHERE STATUS = 'ACTIVE' AND NAME = %s", [module_title])
    rows = cur.fetchall()
    for row in rows:
	number_of_questions = row['NUM_QUIZ_QUESTIONS']
    conn.close()
    return number_of_questions

def get_total_number_of_slides():
    """ get the total number of slides per module """
    total_slides = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("Select MODULE_ID, NUM_SLIDES + NUM_QUIZ_QUESTIONS + NUM_INT_QUESTIONS AS TOTAL_SLIDES FROM MODULES WHERE STATUS = 'ACTIVE'" )
    rows = cur.fetchall()
    for row in rows:
        total_slides.append(row)
    conn.close()
    return total_slides

def check_quiz_answer_exists(uid, qid):
    """ validate that the user has answered a questions """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("Select * FROM GRADEBOOK WHERE USER_ID = %s AND QUESTION_ID = %s AND QUESTION_TYPE = %s",
	    [uid, qid, "QUIZ"])
    if cur.rowcount == 1:
	return True
    return False

def check_quiz_answer_valid(qid, aid):
    """ check that the answer to a question exists in the database """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("Select * FROM QUIZ_ANSWERS WHERE QUESTION_ID = %s AND ANSWER_ID = %s",
	    [qid, aid])
    if cur.rowcount == 1:
	return True
    return False

def add_answer_to_gradebook(uid, orgunit, qid, aid, question_type):
    """ log the users answer to a quiz question in the database """
    conn = do_mysql_connect()
    cur = conn.cursor()
    try:
	cur.execute("INSERT INTO GRADEBOOK (USER_ID, ORG_UNIT, QUESTION_TYPE, QUESTION_ID, ANSWER_ID) VALUES (%s, %s, %s, %s, %s)", 
		[uid, orgunit, question_type, qid, aid])
	conn.commit()
	return 0
    except MySQLdb.Error as e:
	conn.rollback()
    conn.close()

def check_quiz_answer_correct(aid):
    """ check if a specific quiz answer is the correct answer to a question """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("Select * FROM QUIZ_CORRECT WHERE ANSWER_ID = %s", [aid])
    if cur.rowcount == 1:
	return True
    return False

def log_user_quiz_answer(uid, dn, qid, aid, question_type):
    """ validate the user's answers before adding to the gradebook """
    if not check_quiz_answer_exists(uid, qid):
	if check_quiz_answer_valid(qid, aid):
	    orgunit = dn[0].split(",")[1][3:]
	    add_answer_to_gradebook(uid, orgunit, qid, aid, question_type)
	    if check_quiz_answer_correct(aid):
		return 0
	    return 1
    return -1

def check_int_answer_exists(uid, qid):
    """ check that the interactive section answer exists in the database """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("Select * FROM GRADEBOOK WHERE USER_ID = %s AND QUESTION_ID = %s AND QUESTION_TYPE = %s",
	    [uid, qid, "INTERACTIVE"])
    if cur.rowcount == 1:
	return True
    return False

def check_int_answer_correct(aid):
    """ check that the interactive section answer is correct """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("Select * FROM INTERACTIVE_CORRECT WHERE INT_ANS_ID = %s", [aid])
    if cur.rowcount == 1:
	return True
    return False

def get_correct_msg(qid):
    """ get the message to display when the interactive section answer is correct """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM INTERACTIVE_QUESTIONS WHERE INT_Q_ID = %s", [qid])
    row = cur.fetchone()
    conn.close()
    return row['CORRECT_MESSAGE']

def get_incorrect_msg(qid):
    """ get the message to display when the interactive section answer is incorrect """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM INTERACTIVE_QUESTIONS WHERE INT_Q_ID = %s", [qid])
    row = cur.fetchone()
    conn.close()
    return row['INCORRECT_MESSAGE']

def delete_quiz_question(qid):
    """ delete a quiz question and all its answers from the database """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM QUIZ_CORRECT WHERE QUESTION_ID = %s", [qid])
    cur.execute("DELETE FROM QUIZ_ANSWERS WHERE QUESTION_ID = %s", [qid])
    cur.execute("DELETE FROM QUIZ_QUESTIONS WHERE QUESTION_ID = %s", [qid])
    conn.close()
    return 0

def delete_int_question(qid):
    """delete an interactive section question and all its answers """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM INTERACTIVE_CORRECT WHERE INT_Q_ID = %s", [qid])
    cur.execute("DELETE FROM INTERACTIVE_ANSWERS WHERE INT_Q_ID = %s", [qid])
    cur.execute("DELETE FROM INTERACTIVE_QUESTIONS WHERE INT_Q_ID = %s", [qid])
    conn.close()
    return 0

def log_user_int_answer(uid, dn, qid, aid, question_type):
    """ validate the user's answers to an interactive section before adding to the gradebook """
    if not check_int_answer_exists(uid, qid):
	orgunit = dn[0].split(",")[1][3:]
	add_answer_to_gradebook(uid, orgunit, qid, aid, question_type)
	correct = get_correct_msg(qid)
	incorrect = get_incorrect_msg(qid)
	if check_int_answer_correct(aid):
	    return [0, correct]
	return [1, incorrect]
    return [-1, "You have already answered this question."]

def check_module_started(username, mid):
    """ check whether a module was started by a user or not """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("Select * FROM USER_PROGRESS WHERE USER_ID = %s AND MODULE_ID = %s", [username, mid])
    if cur.rowcount == 1:
	return True
    return False

def get_last_viewed_slide(username, mid):
    """ get the number of the last viewed slide for a module """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT LAST_VIEWED FROM USER_PROGRESS WHERE USER_ID = %s AND MODULE_ID = %s", [username, mid])
    row = cur.fetchone()
    conn.close()
    return row['LAST_VIEWED']
    pass

def log_user_progress(username, mid, slide):
    """ log the progress of a user through the slides of a course """
    conn = do_mysql_connect()
    cur = conn.cursor()
    if check_module_started(username, mid):
	last = get_last_viewed_slide(username, mid)
	if slide == (last + 1):
	    cur.execute("UPDATE USER_PROGRESS SET LAST_VIEWED = %s WHERE MODULE_ID = %s AND USER_ID = %s", [slide, mid, username])
    else:
	cur.execute("INSERT INTO USER_PROGRESS (LAST_VIEWED, MODULE_ID, USER_ID) VALUES (%s, %s, %s)", [slide, mid, username])
    conn.commit()
    conn.close()

# QUERIES FOR GETTING INFORMATION ABOUT ADMIN-RELATED THINGS
def get_admin_user_list():
    """ get list of administrators """
    admin = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT user_id,name,unit_ID FROM ADMIN")
    for row in cur.fetchall():
	admin.append(row)
    conn.close()
    return admin

def get_org_unit_info():
    """ get information about orgunits """
    org_units = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT UNIT_ID, UNIT_NAME FROM ORG_UNITS")
    for row in cur.fetchall():
	org_units.append(row)
    conn.close()
    return org_units

def get_data_for_csv(num, filters):
    """ generate data to be converted into csv as requested by user """
    data = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    sql = "SELECT * FROM vw_USER_QUIZ_ANSWERS"
    if num >= 1:
	attrs = list(filters.keys())
	for attr in attrs:
	    if attr == attrs[0]:
		sql += (" WHERE " + attr + " = " + filters[attr] + " ")
	    else:
		sql += ("AND " + attr + " = " + filters[attr] + " ")
    cur.execute(sql)
    for row in cur.fetchall():
	data.append(row)
    conn.close()
    if len(data) >= 1:
	return data
    return None

def check_admin_exists(admin_id):
    """ check that an administrator exists """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ADMIN WHERE USER_ID = %s", [admin_id])
    if cur.rowcount == 1:
	return True
    return False

def get_all_read_perms():
    """ get all read admin permissions  """
    read_perms = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT User_ID FROM ADMIN_PERM WHERE PERMISSION='read'")

    for row in cur.fetchall():
	read_perms.append(row['User_ID'])

    conn.close()
    return read_perms

def get_all_write_perms():
    """ get all write admin permissions  """
    write_perms = list()
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT User_ID FROM ADMIN_PERM WHERE PERMISSION = 'write'")

    for row in cur.fetchall():
        write_perms.append(row['User_ID'])

    conn.close()
    return write_perms

def check_admin_perms(admin_id, permission_type):
    """ check that an administrator has the specified permission """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ADMIN_PERM WHERE USER_ID = %s AND PERMISSION = %s",
	    [admin_id, permission_type])
    if cur.rowcount==1:
	return True
    return False

def check_orgunit_exists(orgunit):
    """ check that an orgunit exists in the database """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ORG_UNITS WHERE UNIT_ID = %s", [orgunit])
    if cur.rowcount == 1:
	return True
    return False

def update_quiz_answer_value(aid, new_value):
    """ update an already existing answer to a quiz question """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("UPDATE QUIZ_ANSWERS SET ANSWER = %s WHERE ANSWER_ID = %s", 
	    [new_value, aid])
    conn.commit()
    conn.close()
    return 0

def update_quiz_question_value(qid, new_value):
    """ update an already existing question to of a quiz """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("UPDATE QUIZ_QUESTIONS SET QUESTION = %s WHERE QUESTION_ID = %s", 
	    [new_value, qid])
    conn.commit()
    conn.close()
    return 0

def update_int_question_value(qid, new_value):
    """ update an already existing interactive section question """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("UPDATE INTERACTIVE_QUESTIONS SET QUESTION = %s WHERE INT_Q_ID = %s", 
	    [new_value, qid])
    conn.commit()
    conn.close()
    return 0

def update_int_answer_value(aid, new_value):
    """ update an already existing interactive section answer to a question """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("UPDATE INTERACTIVE_ANSWERS SET ANSWER = %s WHERE INT_ANS_ID = %s", 
	    [new_value, aid])
    conn.commit()
    conn.close()
    return 0

def update_int_q_correct(qid, aid):
    """ set a new correct answert to an interactive section question """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("UPDATE INTERACTIVE_CORRECT SET INT_ANS_ID = %s WHERE INT_Q_ID = %s", 
	    [aid, qid])
    conn.commit()
    conn.close()
    return 0

def update_num_slides(module_id, num_slides):
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("UPDATE MODULES SET NUM_SLIDES = %s WHERE MODULE_ID = %s", 
	    [num_slides, module_id])
    conn.commit()
    conn.close()
    return 0

def add_perm(uid, perm_type):
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO ADMIN_PERM (USER_ID, PERMISSION) VALUES (%s, %s)", 
	    [uid, perm_type])
    conn.commit()
    conn.close()
    return 0

def remove_perm(uid, perm_type):
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM ADMIN_PERM WHERE USER_ID = %s AND PERMISSION = %s", 
	    [uid, perm_type])
    conn.commit()
    conn.close()
    return 0

def delete_admin(uid):
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM ADMIN_PERM WHERE USER_ID = %s", [uid])
    cur.execute("DELETE FROM ADMIN WHERE USER_ID = %s", [uid])
    conn.commit()
    conn.close()
    return 0

def update_q_correct(qid, aid):
    """ set a new correct answer to quiz question """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("UPDATE QUIZ_CORRECT SET ANSWER_ID = %s WHERE QUESTION_ID = %s", 
	    [aid, qid])
    conn.commit()
    conn.close()
    return 0

def update_int_correct_value(qid, new_value):
    """ update the message to be displayed in case the user answer to an
        interactive section question is incorrect """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("UPDATE INTERACTIVE_QUESTIONS SET CORRECT_MESSAGE = %s WHERE INT_Q_ID = %s", 
	    [new_value, qid])
    conn.commit()
    conn.close()
    return 0

def update_int_incorrect_value(qid, new_value):
    """ update the message to be displayed in case the user answer to an
	interactive section question is incorrect """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("UPDATE INTERACTIVE_QUESTIONS SET INCORRECT_MESSAGE = %s WHERE INT_Q_ID = %s", 
	    [new_value, qid])
    conn.commit()
    conn.close()
    return 0

def update_max_q_num(mid):
    """ update the maximum number of quiz questions """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("UPDATE MODULES SET NUM_QUIZ_QUESTIONS = NUM_QUIZ_QUESTIONS + 1 WHERE MODULE_ID = %s", 
	    [mid])
    conn.commit()
    conn.close()
    return 0

def add_new_question(mid, new_question):
    """ add a new question to a module quiz """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO QUIZ_QUESTIONS (MODULE_ID, QUESTION) VALUES (%s, %s)", 
	    [mid, new_question])
    new_q_id = cur.lastrowid
    conn.commit()
    conn.close()
    update_max_q_num(mid)
    return new_q_id

def add_new_answer(qid, new_answer):
    """ add a new answer to a quiz questions """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO QUIZ_ANSWERS (QUESTION_ID, ANSWER) VALUES (%s, %s)", 
	    [qid, new_answer])
    new_ans_id = cur.lastrowid
    conn.commit()
    conn.close()
    return new_ans_id

def add_new_correct_answer(qid, aid):
    """ add a new correct answer to a quiz question """
    conn = do_mysql_connect()
    cur = conn.cursor()
    # put some checks in m8
    cur.execute("INSERT INTO QUIZ_CORRECT (QUESTION_ID, ANSWER_ID) VALUES (%s, %s)", 
	    [qid, aid])
    new_ans_id = cur.lastrowid
    conn.commit()
    conn.close()
    return 0

def update_max_i_num(mid):
    """ update the maximum number of interactive section questions """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("UPDATE MODULES SET NUM_INT_QUESTIONS = NUM_INT_QUESTIONS + 1 WHERE MODULE_ID = %s", 
	    [mid])
    conn.commit()
    conn.close()
    return 0

def add_new_int_question(mid, new_question, img_link, correct_msg, incorrect_msg):
    """ add a new question to an interactive section """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO INTERACTIVE_QUESTIONS (MODULE_ID, QUESTION, MEDIA_LINK, MEDIA_TYPE, CORRECT_MESSAGE, INCORRECT_MESSAGE) VALUES (%s, %s, %s, %s, %s, %s)", 
	    [mid, new_question, img_link, "IMG", correct_msg, incorrect_msg])
    new_q_id = cur.lastrowid
    conn.commit()
    conn.close()
    return new_q_id

def add_new_int_answer(qid, new_answer):
    """ add new answers to an interactive section """
    conn = do_mysql_connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO INTERACTIVE_ANSWERS (INT_Q_ID, ANSWER) VALUES (%s, %s)", 
	    [qid, new_answer])
    new_ans_id = cur.lastrowid
    conn.commit()
    conn.close()
    return new_ans_id

def add_new_correct_int_answer(qid, aid):
    """ add a new correct answer to an interactive section  """
    conn = do_mysql_connect()
    cur = conn.cursor()
    # put some checks in m8
    cur.execute("INSERT INTO INTERACTIVE_CORRECT (INT_Q_ID, INT_ANS_ID) VALUES (%s, %s)", 
	    [qid, aid])
    new_ans_id = cur.lastrowid
    conn.commit()
    conn.close()
    return 0

def do_admin_add(admin_id):
    """ add a user to the administrator list """
    conn = do_mysql_connect()
    cur = conn.cursor()
    orgunit = randrange(1,500) #artificially generating orgunit, get value from ldap
    do_add_orgunit(orgunit)
    if not check_admin_exists(admin_id):
        try:
            cur.execute("INSERT INTO ADMIN (USER_ID, NAME, UNIT_ID) VALUES (%s, %s, %s)", 
        	    [admin_id, people_names[randrange(0,len(people_names))], orgunit])
            conn.commit()
            return 0
        except MySQLdb.Error as e:
            conn.rollback()
	    return e
    conn.close()
    return -1

def do_add_orgunit(orgunit):
    """ add a new orgunit """
    conn = do_mysql_connect()
    cur = conn.cursor()
    if not check_orgunit_exists(orgunit):
        try:
            cur.execute("INSERT INTO ORG_UNITS (UNIT_ID, UNIT_NAME) VALUES (%s, %s)", 
        	    [orgunit, unit_names[randrange(0,len(unit_names))]])
            conn.commit()
            return 0
        except MySQLdb.Error as e:
            conn.rollback()
    conn.close()
    return -1

def do_admin_add_perms(admin_id, permission):
    """ add permissions for a specified user """
    conn = do_mysql_connect()
    cur = conn.cursor()
    if not check_admin_perms(admin_id, permission):
	try:
	    cur.execute("INSERT INTO ADMIN_PERM (USER_ID, PERMISSION) VALUES (%s, %s)", 
		    [admin_id, permission])
	    conn.commit()
	    return 0
	except MySQLdb.Error as e:
	    conn.rollback()
    conn.close()
    return -1

# DATABASE CONNECTION

def read_mysql_password():
    """ reads password from file """
    f = open('mysql.passwd', 'r')
    passwd = f.read()
    f.close()
    return passwd.rstrip()

def do_mysql_connect():
    """ connect to the database """
    conn = MySQLdb.connect(db='auscats', host='localhost', port=3306, 
	    user='flask', passwd=read_mysql_password(), 
	    cursorclass=MySQLdb.cursors.DictCursor)
    return conn

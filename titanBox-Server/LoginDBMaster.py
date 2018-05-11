import mysql.connector
from werkzeug.security import check_password_hash,generate_password_hash

db_config = {'host' :'localhost',
             'user':'admin',
             'password':'551996',
             'database':'titanBox'}

conn = mysql.connector.connect(**db_config)
cur = conn.cursor()
cur.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

def is_a_valid_user(username):
    """This function will check whether user identified by username is in LoginDetails table or not"""
    query = """select count(*)
               from LoginDetails
               where username = %s"""
    cur.execute(query,(username,))
    res = cur.fetchone()
    return bool(res[0])

def check(username,password):
    """This function will check whether password is correct or not
        Username must be valid"""
    query = """select password_hash
               from LoginDetails
               where username=%s"""
    cur.execute(query,(username,))
    res = cur.fetchone()
    return check_password_hash(res[0],password)


def logged_in_somewhere(username):
    """This function will tell whether user identified by username is logged in from somewhere else or not"""
    query = """select count(*)
                from LoggedIn
                where id = (select id
                            from LoginDetails
                            where username = %s)"""
    cur.execute(query,(username,))
    res = cur.fetchone()
    return bool(res[0])

def another_user_logged_in(ipv4_addr):
    """This function will return true if some other user logged on this machine"""
    query = """select count(*)
                from LoggedIn
                where ipv4_addr = %s"""
    cur.execute(query,(ipv4_addr,))
    res = cur.fetchone()
    return bool(res[0])

def login(username,ipv4_addr):
    """This function will make an entry into LoggedIn table"""
    query = """select id
                from LoginDetails
                where username = %s"""
    cur.execute(query,(username,))
    res = cur.fetchone()
    query = """insert into LoggedIn
                values(%s,%s)"""
    cur.execute(query,(int(res[0]),ipv4_addr,))
    conn.commit()

def make_an_entry(username,password):
    """This function will make an entry into LoginDetails table"""
    query = """insert into LoginDetails(username,password_hash)
                values(%s,%s)"""
    cur.execute(query,(username,generate_password_hash(password),))
    conn.commit()

def username(ipv4_addr):
    """This function will return username given ipv4 address"""
    query = """select username
                from LoginDetails
                where id = (select id
                            from LoggedIn
                            where ipv4_addr = %s)"""
    cur.execute(query,(ipv4_addr,))
    res = cur.fetchone()
    if res == None :
        return "Nobody"
    return res[0]

def no_of_users():
    """This function will return number of entries in LoginDetails"""
    query = """select count(*)
                from LoginDetails"""
    cur.execute(query)
    res = cur.fetchone()
    return res[0]

def no_of_active_users():
    """This function will return number of entries in LoggedIn table"""
    query = """select count(*)
                from LoggedIn"""
    cur.execute(query)
    res = cur.fetchone()
    return res[0]

def logout(ipv4_addr):
    """This function will delete an entry from LoggedIn table"""
    query = """delete from LoggedIn
                where ipv4_addr = %s"""
    cur.execute(query,(ipv4_addr,))
    conn.commit()

def reset():
    """This function will clear all tables"""
    query = """delete from KeyStore"""

    cur.execute(query)
    conn.commit()

    query = """delete from Blocks"""

    cur.execute(query)
    conn.commit()

    query = """delete from EncryptionKeys"""

    cur.execute(query)
    conn.commit()

    query = """delete from BlockBelongsTo"""

    cur.execute(query)
    conn.commit()

    query = """delete from FileBelongsTo"""

    cur.execute(query)
    conn.commit()

    query = """delete from Files"""

    cur.execute(query)
    conn.commit()

    query = """delete from LoggedIn"""

    cur.execute(query)
    conn.commit()

    query="""delete from LoginDetails"""

    cur.execute(query)
    conn.commit()


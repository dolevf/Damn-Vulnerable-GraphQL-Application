import sys
import os
import shutil
import config
import random

from app import db
from dvga.models import *
from stuffing import *



def clean_up():
    if os.path.exists(config.WEB_UPLOADDIR):
        shutil.rmtree(config.WEB_UPLOADDIR)
        os.mkdir(config.WEB_UPLOADDIR)
    else:
        os.mkdir(config.WEB_UPLOADDIR)

    print('Reconstructing Database')
    if os.path.exists(config.SQLALCHEMY_FILE):
        try:
            os.remove(config.SQLALCHEMY_FILE)
        except OSError as err:
            print("[-] Error during cleanup: ", err)
    return


def pump_db():
    db.create_all()

    # Users we want to make sure to have
    users = [
                User(username="admin",   password='123456',  roles='user,moderator,admin',  email="admin@dvga.com"),
                User(username="mak",     password='123456',  roles='user,moderator',        email="mak@dvga.com"),
                User(username="bob",     password='123456',  roles='user',                  email="bob@dvga.com"),
                User(username="eva",     password='123456',  roles='user',                  email="eva@dvga.com"),
            ]  
    
    for u in users:
        db.session.add(u)

    # Creating pastes to test getting pastes by username
    mak =                  users[1]
    audit =                Audit()
    paste =                Paste()
    paste.title =          random.choice(titles)
    paste.content =        "Mak's stuff number 2"
    paste.public =         False
    paste.user_id =        mak.id
    paste.user =           mak
    paste.ip_addr =        '127.0.0.1'
    paste.user_agent =     'User-Agent not set'
    audit.gqloperation =   'CreateTestPaste for user mak'

    db.session.add(paste)

    # Creating pastes to test non moderator role
    bob =                  users[2]
    audit =                Audit()
    paste =                Paste()
    paste.title =          random.choice(titles)
    paste.content =        "Bob's stuff number"
    paste.public =         False
    paste.user_id =        bob.id
    paste.user =           bob
    paste.ip_addr =        '127.0.0.1'
    paste.user_agent =     'User-Agent not set'
    audit.gqloperation =   'CreateTestPaste for user bob'

    db.session.add(paste)

    # Other users to fill up database
    stuffing_users = []
    for _ in range(0, 10):
        username = random.choice(usernames)
        u = User(
                username =  username,
                password =  random.choice(weak_passwords),
                roles = 'user',
                email = username + "@dvga.com",
            )
        stuffing_users.append(u)
        db.session.add(u)

    # Creating content
    for _ in range(0, 30):
        p =                 Paste()
        user =              random.choice(stuffing_users)        
        p.user_id =         user.id
        p.user =            user
        p.public =          True
        p.title =           random.choice(titles)
        p.content =         random.choice(content)
        p.ip_addr =         random.choice(ip_addresses)
        p.user_agent =      random.choice(agents)
        db.session.add(p)

    db.session.commit()

if __name__ == '__main__':
  clean_up()
  pump_db()
  sys.exit()
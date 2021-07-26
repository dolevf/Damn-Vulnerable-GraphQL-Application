import datetime
from app import db


# Models
class User(db.Model):
    __tablename__ = 'users'
    id =        db.Column(db.Integer,    primary_key=True)
    username =  db.Column(db.String(20), unique=False, nullable=False)
    password =  db.Column(db.String(20), nullable=False)
    roles =     db.Column(db.String(30), default="user")
    paste =     db.relationship('Paste', backref='User', lazy='dynamic')
    
    @classmethod
    def create_user(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()
        return obj

    # TODO add complet CRUD classmethods for this object


class Paste(db.Model):
    __tablename__ = 'pastes'
    id =            db.Column(db.Integer,    primary_key=True)
    title =         db.Column(db.String)
    content =       db.Column(db.String)
    public =        db.Column(db.Boolean,    default=False)
    user_agent =    db.Column(db.String,     default=None)
    ip_addr =       db.Column(db.String)
    burn =          db.Column(db.Boolean,    default=False)
    user_id =       db.Column(db.Integer,    db.ForeignKey(User.id))
    user =          db.relationship(User,    backref='pastes')

    @classmethod
    def create_paste(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()
        return obj





class Audit(db.Model):
    __tablename__ = 'audits'
    id =            db.Column(db.Integer, primary_key=True)
    gqloperation =  db.Column(db.String)
    timestamp =     db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @classmethod
    def create_audit_entry(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()
        return obj
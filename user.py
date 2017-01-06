from flask_sqlalchemy import orm


def create_user_class(db):
    class User(db.Model):
        # DB Setup
        __tablename__ = "users"
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(32), unique=True)
        public_key = db.Column(db.String(1024))


        def to_dict(self):
            return {"username": self.username,
                    "public_key": self.public_key}



    return User



class UserManager(object):

    def __init__(self, db, User):
        self.db = db
        self.User = User

    def add(self, **kwargs):
        username = kwargs['username'][0]
        public_key = kwargs['public_key'][0]
        ip = None
        if 'ip' in kwargs:
            ip = kwargs['ip'][0]
        user = self.User(username=username,
                         public_key=public_key)
        user.ip = ip
        self.db.session.add(user)
        self.db.session.commit()

    def get(self, **kwargs):
        username = kwargs['username']
        return self.db.session.query(self.User).filter_by(username=username).first()



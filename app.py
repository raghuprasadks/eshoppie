from flask import Flask, render_template, url_for, request, redirect,jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_jwt_extended import JWTManager
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt,set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies)
from passlib.hash import pbkdf2_sha256 as sha256



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eshoppingnew.db'
db = SQLAlchemy(app)


app.config['JWT_SECRET_KEY'] = 'eshoppy@1234'
# Configure application to store JWTs in cookies
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
# Only allow JWT cookies to be sent over https. In production, this
# should likely be True
app.config['JWT_COOKIE_SECURE'] = False

#app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
#app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

# Enable csrf double submit protection. See this for a thorough
# explanation: http://www.redotheweb.com/2015/11/09/api-security.html
#app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_CSRF_CHECK_FORM'] = True

jwt = JWTManager(app)

app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    mobile = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)
    
    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)
    
    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email = email).first()
   

    def __repr__(self):
        return '<Registration %r>' % self.id
    
'''
class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key = True)
    jti = db.Column(db.String(120))
    
    def add(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)

'''

@app.route('/', methods=['POST', 'GET'])
def index():
    
    info = {}
    
    if request.method == 'POST':
        reg_name = request.form['name']
        reg_mobile = request.form['mobile']
        reg_email = request.form['email']
        reg_password = request.form['password']
        passwordhash = Registration.generate_hash(reg_password)        
        new_registration = Registration(name=reg_name,mobile=reg_mobile,email=reg_email,password=passwordhash)
        
        print('Password hashed :',passwordhash)
        
        try:
            db.session.add(new_registration)
            db.session.commit()
            print("Data committed")
            
            access_token = create_access_token(identity = reg_email)
            refresh_token = create_refresh_token(identity = reg_email)
            print('Access token ',access_token)
            print('Refersh token ',refresh_token)            
            #resp = make_response(redirect('/',302))
            info = {
                'message': 'Thanks for registering with us {} '.format(reg_name),
                'access_token': access_token,
                'refresh_token': refresh_token
                }
            resp = make_response(render_template('index.html',info=info))
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            return resp
            # Set the JWTs and the CSRF double submit protection cookies
            # in this response
            '''
            resp = jsonify({'Register': True})
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            info = {
                'message': 'Thanks for registering with us {} '.format(reg_name),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'resp':resp
                }
            print("Info ",info)
            '''
            #return render_template('index.html',info=info)
        except Exception as e:
            print(e)
            return 'There was an issue in registering'
    else:
        
            
        return render_template('index.html',info=info)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        reg_email = request.form['email']
        reg_password = request.form['password']
        
        current_user = Registration.find_by_email(reg_email)

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(reg_email)}
               
        
        if Registration.verify_hash(reg_password, current_user.password):
            access_token = create_access_token(identity = reg_email)
            refresh_token = create_refresh_token(identity = reg_email)
            info= {
                'message': 'Welcome {}'.format(current_user.name),
                'access_token': access_token,
                'refresh_token': refresh_token
                }
            print("login :info ",info)
            return render_template('chat.html',info=info)
            
        else:
            info = {'message': 'Wrong credentials'}
            return render_template('login.html')
    
    else:
        return render_template('login.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if request.method == 'POST':
        print('logout')
        resp = make_response(render_template('/logout.html'))
        unset_jwt_cookies(resp)
        return resp
        
if __name__ == "__main__":
    app.run(debug=True)

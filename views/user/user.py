from flask import Flask,session,render_template,redirect,Blueprint,request
from utils.errorResponse import *
import time
from utils.query import querys
ub = Blueprint('user',__name__,url_prefix='/user',template_folder='templates')

@ub.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        request.form = dict(request.form)

        def filter_fns(item):
            return request.form['username'] in item and request.form['password'] in item

        users = querys('select * from user', [], 'select')
        login_success = list(filter(filter_fns, users))
        if not len(login_success):
            return errorResponse('输入的密码或账号出现问题')

        session['username'] = request.form['username']
        session['createTime'] = login_success[0][-1]
        return redirect('/page/home', 301)
    else:
        return render_template('login.html')



@ub.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        request.form = dict(request.form)
        if request.form['password'] != request.form['passwordCheked']:
            return '两次密码不符'
        else:
            def filter_fn(item):
                return request.form['username'] in item

            users = querys('select * from user', [], 'select')
            filter_list = list(filter(filter_fn, users))
            if len(filter_list):
                return errorResponse('该用户名已被注册')
            else:
                time_tuple = time.localtime(time.time())
                querys('insert into user(username,password,createTime) values(%s,%s,%s)',
                       [request.form['username'], request.form['password'],
                        str(time_tuple[0]) + '-' + str(time_tuple[1]) + '-' + str(time_tuple[2])])

        return redirect('/user/login', 301)

    else:
        return render_template('register.html')

@ub.route('/logOut',methods=['GET','POST'])
def logOut():
    session.clear()
    return redirect('/user/login')
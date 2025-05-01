from flask import Flask, session, render_template, redirect, request
import re

app = Flask(__name__)
app.secret_key = 'This is a app.secret_Key , You Know ?'

from views.page import page
from views.user import user

app.register_blueprint(page.pb)
app.register_blueprint(user.ub)


# 首页直接重定向到登录页
@app.route('/')
def index():
    return redirect('/user/login')


# 登录状态检查
def is_user_logged_in():
    return session.get('username') is not None


@app.before_request
def before_request():
    # 不需要验证静态资源的请求
    if request.path.startswith('/static'):
        return None

    # 允许访问登录和注册页面
    if request.path in ['/user/login', '/user/register']:
        return None

    # 如果用户未登录，强制跳转到登录页面
    if not is_user_logged_in():
        return redirect('/user/login')
    return None


# 404 错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# 捕获其他未定义路径
@app.route('/<path:path>')
def catch_all(path):
    return redirect('/404')  # 或者是直接返回 '404.html' 页面


if __name__ == '__main__':
    app.run(debug=True)  # 开启调试模式以便于开发时查看错误

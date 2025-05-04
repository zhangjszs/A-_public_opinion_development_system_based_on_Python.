from flask import Flask, session, render_template, redirect, request
from flask_debugtoolbar import DebugToolbarExtension
import re

app = Flask(__name__)
# 保留你原来的 secret_key
app.secret_key = 'This is a app.secret_Key , You Know ?'

# 开启调试模式
app.debug = True
# 不拦截 302 重定向，页面将像平常那样直接跳转
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# 初始化 DebugToolbar
toolbar = DebugToolbarExtension(app)

# 注册蓝图
from views.page import page
from views.user import user

app.register_blueprint(page.pb)
app.register_blueprint(user.ub)

# 首页直接重定向到登录页
@app.route('/')
def index():
    return redirect('/user/login')

# 登录状态检查函数
def is_user_logged_in():
    return session.get('username') is not None

# 全局请求前钩子：静态资源和登录/注册页不拦截，未登录的其他请求强制跳转到登录页
@app.before_request
def before_request():
    if request.path.startswith('/static'):
        return None
    if request.path in ['/user/login', '/user/register']:
        return None
    if not is_user_logged_in():
        return redirect('/user/login')
    return None

# 404 错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# 捕获其他未定义路径，跳转到 404
@app.route('/<path:path>')
def catch_all(path):
    return redirect('/404')

if __name__ == '__main__':
    # debug=True 会自动重载代码，并配合 DebugToolbar 使用
    app.run(debug=True)

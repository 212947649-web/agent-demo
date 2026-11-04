import os
from flask import Flask, request, redirect, session, render_template_string
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "demo-secret"
USER, PASS = "泽", "123456"
client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

LOGIN = """
<!doctype html><title>登录</title>
<h2>登录</h2>
<form method="post">
用户名 <input name="u"><br>
密码 <input name="p" type="password"><br>
<button>登录</button>
</form>
{% if err %}<p style="color:red">{{ err }}</p>{% endif %}
"""

HOME = """
<!doctype html><title>小助手</title>
<p>你好，{{ name }} <a href="/logout">退出</a></p>
<form method="post">
<input name="q" style="width:320px">
<button>发送</button>
</form>
{% if a %}<p><b>回答：</b>{{ a }}</p>{% endif %}
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    err = ""
    if request.method == "POST":
        if request.form.get("u") == USER and request.form.get("p") == PASS:
            session["user"] = USER
            return redirect("/")
        err = "账号或密码错"
    return render_template_string(LOGIN, err=err)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect("/login")
    q = a = ""
    if request.method == "POST":
        q = request.form.get("q", "")
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": q}],
        )
        a = resp.choices[0].message.content
    return render_template_string(HOME, name=session["user"], a=a)

if __name__ == "__main__":
    app.run(port=5000)
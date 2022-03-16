# Flaskクラスのimport
# from crypt import methods
# loggingをimportする
import logging
import os
from email_validator import validate_email, EmailNotValidError
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import mail

# import文が長くなるため改行
from flask import (
    Flask,
    current_app,
    g,
    redirect,
    render_template,
    request,
    url_for,
    flash,
)

# Flaskクラスのインスタンス化
app = Flask(__name__)

# 秘密鍵(SECRET_KEY)を追加する
app.config["SECRET_KEY"] = "gvidmsfgs1iegs1bk66m"

# ログレベルを設定する
app.logger.setLevel(logging.DEBUG)

# リダイレクトの中断対策
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

# DebugToolbarExtensionにアプリケーションをセットする
toolbar = DebugToolbarExtension(app)

# Mailクラスのコンフィグを追加
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT")
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS")
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

# flask-mail拡張を登録する
mail = Mail(app)

# # URIと実行する関数のマッピング
# @app.route("/")
# def index():
#     return "Hello, Flaskbook!"

# # ルーティング(リクエスト先URIと関数の紐づけ)追加
# @app.route("/hello/<name>", methods=["GET", "POST"], endpoint="hello-endpoint")
# def hello(name):
#     # Python 3.6から導入されたf-stringで文字列を定義
#     return f"Hello, {name}!"


# # show_nameエンドポイントを作成する
# @app.route("/name/<name>")
# def show_name(name):
#     # 変数をテンプレートエンジンに渡す
#     return render_template("index.html", name=name)


# with app.test_request_context():
#     # /
#     print(url_for("index"))
#     # /hello/world
#     print(url_for("hello-endpoint", name="world"))
#     # /name/ichiro?page=ichiro
#     print(url_for("show_name", name="ichiro", page="1"))

#     # ここで呼び出すとエラー
#     print(current_app)

#     # アプリケーションコンテキストを取得してスタックへpush
#     ctx = app.app_context()
#     ctx.push()

#     # current_appにアクセスが可能になる
#     print(current_app.name)
#     # >> apps.minimalapp.app

#     # グローバルなテンポラリ領域に値を設定する
#     g.connection = "connection"
#     print(g.connection)
#     # >> connection

# with app.test_request_context("/users?updated=true"):
#   # trueが出力される
#   print(request.args.get("updated"))


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/contact/complete", methods=["GET", "POST"])
def contact_complete():
    if request.method == "POST":
        # form属性を使ってフォームの値を取得する
        username = request.form["username"]
        email = request.form["email"]
        description = request.form["description"]

        # 入力チェック
        is_valid = True

        if not username:
            flash("ユーザ名は必須です")
            is_valid = False

        if not email:
            flash("メールアドレスは必須です")
            is_valid = False

        try:
            validate_email(email)
        except EmailNotValidError:
            flash("メールアドレスの形式で入力してください")
            is_valid = False

        if not description:
            flash("問い合わせ内容は必須です")

        if not is_valid:
            return redirect(url_for("contact"))
        # メール送信(最後に実装する)

        # 問い合わせ完了エンドポイントへリダイレクトする
        flash("問い合わせありがとうございました。")
        return redirect(url_for("contact_complete"))

    return render_template("contact_complete.html")


# Flask 2 からは@ app. get("/ hello")、@ app. post("/ hello") と 記述 する こと が 可能
# @app. get("/ hello")
# @app. post("/ hello")
# def hello():
# return "Hello, World!"

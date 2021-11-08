from psycopg2 import Error
from flask import Flask, render_template, request
import starwars_db

app = Flask(__name__)

# Создание бд и выгрузка данных
starwars_db.first_setup_app()

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/top')
def top():
    data_c = starwars_db.pull_data_from_starships_ordered()
    return render_template("top.html", db_data=data_c)


@app.route('/characters')
def characters():
    data_c = starwars_db.pull_data_from_characters()
    return render_template("characters.html", db_data=data_c)


@app.route('/starships')
def starships():
    data_c = starwars_db.pull_data_from_starships()
    return render_template("starships.html", db_data=data_c)


@app.route('/updatedb', methods=['POST', 'GET'])
def update_db():
    if request.method == 'POST':
        try:
            starwars_db.update_characters_table()
            starwars_db.update_starships_table()
            return render_template("update_db.html", data_msg="Database updated successfully !")
        except (Exception, Error) as error_db:
            return render_template("update_db.html", data_msg=error_db)

    else:
        return render_template("update_db.html", data_msg="Updating data from source open API https://swapi.dev/")


if __name__ == "__main__":
    app.run(host='0.0.0.0')

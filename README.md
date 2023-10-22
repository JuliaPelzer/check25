# ToDo App with Flask and Tailwind

This is a online ToDo App to test out flask and tailwindcss. Might be used as a base project.

## Setup
setup venv and get python dependencies
```shell
python -m venv .venv
pip install -r requirements.txt
```

initialize dev database
```shell
flask init-db
```

start flask development server
```shell
flask run --debug
```

install tailwindcss with yarn
```shell
yarn install
```

tailwindcss
```shell
npx tailwindcss -i ./app/static/src/input.css -o ./app/static/style.css --watch
```
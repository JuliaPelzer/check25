FROM node

COPY . ./check25/

WORKDIR check25
RUN [ "npm", "install", "yarn" ]
RUN [ "yarn", "install" ]
RUN [ "npx", "tailwindcss", "-i", "./app/static/src/input.css", "-o", "./app/static/style.css" ]


FROM python

COPY --from=0 ./check25/ ./check25/

WORKDIR check25
RUN [ "pip", "install", "-r", "requirements.txt"]
RUN [ "python", "app/backend/setup_db.py"]

CMD [ "python", "-m", "flask", "run", "--host=0.0.0.0" ]


from flaskblog import create_app,start_database

app=create_app()
start_database(app)
if __name__ == '__main__':
    app.run()

from website import create_app

app = create_app()

# Error prevention, makes sure you run the website if and only if you run this file, but not import or anything else
if __name__ == '__main__':
    # runs flask application, start a web server
    # debug=True, everytime things in python file change, we will re-run the web server, on for development, off for production
    app.run(debug=True)

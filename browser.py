#Main file - starts the app

if __name__ == '__main__':
    import src.app as app
    app = app.Browser(800, 600)
    app.run()
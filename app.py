from applications import app
# from waitress import serve

# if __name__ == '__main__':
#     serve(app, host='0.0.0.0', port=5000, threads=16)
if __name__ == '__main__':
    app.debug = True
    app.run()

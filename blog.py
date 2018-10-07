from bottle import route, run, template, static_file


@route('/')
def index():
    return template('index')


@route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')


run(host='localhost', port=8080, reloader=True)

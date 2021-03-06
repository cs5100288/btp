from tornado.options import options, define, parse_command_line
import django.core.handlers.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.web,tornado.websocket
import tornado.wsgi
import sys,os
os.environ['DJANGO_SETTINGS_MODULE']='settings'
import tornado_mappings
from tornado import autoreload

# import __builtin__
# openfiles = set()
# oldfile = __builtin__.file
# class newfile(oldfile):
#     def __init__(self, *args):
#         self.x = args[0]
#         print "### OPENING %s ###" % str(self.x)
#         oldfile.__init__(self, *args)
#         openfiles.add(self)

#     def close(self):
#         print "### CLOSING %s ###" % str(self.x)
#         oldfile.close(self)
#         openfiles.remove(self)
# oldopen = __builtin__.open
# def newopen(*args):
#     return newfile(*args)
# __builtin__.file = newfile
# __builtin__.open = newopen

# def printOpenFiles():
#     print "### %d OPEN FILES: [%s]" % (len(openfiles), ", ".join(f.x for f in openfiles))

def run_tornado_server(p):
    define('port', type=int, default=p)

    class HelloHandler(tornado.web.RequestHandler):
        def get(self):
            self.write('Hello from tornado')

    def main():
        wsgi_app = tornado.wsgi.WSGIContainer(
            django.core.handlers.wsgi.WSGIHandler())
        url_mappings = [
                ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
                ]
        url_mappings = tornado_mappings.tornado_urlpatterns + url_mappings
        tornado_app = tornado.web.Application(url_mappings, debug=True,
            static_path=os.path.join(os.path.dirname(__file__), "Video_Performance", "static")
            )
        server = tornado.httpserver.HTTPServer(tornado_app)
        server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()
    main()


def print_usage():
    print "Usage: python runserver.py env ip:port"
    print "env = dev/prod"
    print "ip= 127.0.0.1 or 0.0.0.0(default)"
    print "port: preferably >=8000. default=8000"


def validate_env(e):
    if e in ["dev", "prod"]:
        return True
    else:
        print_usage()
        sys.exit(1)


def validate_ipport(ipport):
    sp = ipport.split(":")
    if len(sp) == 2:
        ip, port = sp
        try:
            map(int, ip.split("."))
            int(port)
        except Exception:
            print_usage()
            sys.exit(1)
        return True
    else:
        print_usage()
        sys.exit(1)
if __name__ == "__main__":
    ip = "0.0.0.0"
    port = "8000"
    env = "prod"
    l = len(sys.argv)
    if l < 1:
        print_usage()
    if l > 1:
        tempenv = sys.argv[1]
        validate_env(tempenv)
        env = tempenv
    if l > 2:
        ipport = sys.argv[2]
        validate_ipport(tempenv)
    if env == "dev":
        print "Running django development server"
        os.system("python manage.py runserver " + ip + ":" + port)
    else:
        run_tornado_server(int(port))

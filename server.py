from flask import Flask, render_template
from websockets.sync.server import Server
import os
class RobotFlask(Flask):
  def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
    with self.app_context() as f:
        init = f.app.config.get("init")
        if os.getenv('WERKZEUG_RUN_MAIN') != 'true':
            if init != None:
               init(f.app)
        else:
            restart = f.app.config.get("restart")
            if restart != None:
                restart(f.app)
    super(RobotFlask, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)
def webserver(initialize=None, restart=None):
    app = RobotFlask("robot")
    app.config["restart"] = restart
    app.config["init"] = initialize

    @app.route("/")
    def index():
        websocket: Server = getattr(Flask, "_websocket")
        socket_ip = websocket.socket.getsockname()
        return render_template("index.html", websocket_port=socket_ip[1])
    return app

#!/usr/bin/python
import http.server
import json
import sys
import os
import shutil
import datetime

PORT = 8000
HOME = os.environ.get('HOME')

config_html = "./actions-for-nautilus-configurator.html"
config_file = HOME + \
    "/.local/share/nautilus-python/extensions/actions-for-nautilus/config.json"
config_schema = HOME + \
    "/.local/share/nautilus-python/extensions/actions-for-nautilus/actions-for-nautilus.schema.json"
favicon = "./sub-menu.png"

config_html_exists = os.path.exists(config_html)
config_file_exists = os.path.exists(config_file)
config_schema_exists = os.path.exists(config_schema)
favicon_exists = favicon

textual_mimes = [
    "text/html",
    "application/json"
]
docs = {
    "/": {
        "path": config_html,
        "exists": config_html_exists,
        "mimetype": "text/html",
        "default": None
    },
    "/actions-for-nautilus-configurator.html": {
        "path": config_html,
        "exists": config_html_exists,
        "mimetype": "text/html",
        "default": None
    },
    "/config": {
        "path": config_file,
        "exists": config_file_exists,
        "mimetype": "application/json",
        "default": "{\"actions\":[],\"debug\":false}"
    },
    "/schema": {
        "path": config_schema,
        "exists": config_schema_exists,
        "mimetype": "application/json",
        "default": None
    },
    "/favicon.ico": {
        "path": favicon,
        "exists": favicon_exists,
        "mimetype": "image/png",
        "default": None
    }
}


def get_file_content(doc_path):
    doc_data = docs.get(doc_path)
    if doc_data is None or ((not doc_data["exists"]) and doc_data["default"] is None):
        return {
            "error": 404,
            "message": "Not Found"
        }
    textual_data = doc_data["mimetype"] in textual_mimes
    mimetype = doc_data["mimetype"] + "; charset=utf-8" if textual_data else doc_data["mimetype"]

    if not doc_data["exists"]:
        return {
            "mimetype": mimetype,
            "data": doc_data["default"].encode('utf8') if textual_data else doc_data["default"]
        }

    try:
        with open(doc_data["path"], "r" if textual_data else "rb") as f:

            return {
                "mimetype": mimetype,
                "data": f.read().encode('utf8') if textual_data else f.read(-1)
            }
    except:
        return {
            "error": 500,
            "message": "Internal Error"
        }


def backup_file(file_path):
    modified_time = os.path.getmtime(file_path)
    time_stamp = datetime.datetime.fromtimestamp(
        modified_time).strftime("%b-%d-%y-%H:%M:%S")
    shutil.copyfile(file_path, file_path+"_"+time_stamp)


def restart_nautilus(self):
    try:
        os.system("nautilus -q")
        self.send_error(204, "restarted")
    except:
        print("Uh oh - failed to kill nautilus")
        self.send_error(500)
    self.end_headers()
    return


def terminate_server(self):
    self.send_error(204, "terminated")
    self.end_headers()
    self.server.shutdown()
    return


def save_config(self):
    content_type = self.headers.get_content_type()
    content_length = self.headers.get("Content-Length")
    data = ""
    try:
        if content_type == "application/json":
            if content_length is not None and (content_length := int(content_length)) > 0:
                state_message = ""
                try:
                    state_message = "Reading config from request"
                    data = self.rfile.read(content_length)
                    state_message = "Converting config from JSON"
                    message = json.loads(data)
                    if os.path.exists(config_file):
                        state_message = "Backing up existing config file"
                        backup_file(config_file)
                    state_message = "Preparing to update config file"
                    with open(config_file, 'w') as f:
                        state_message = "Updating config file"
                        f.write(json.dumps(message))
                    docs["/config"]["exists"] = True
                    self.send_error(204)
                except:
                    print("Uh oh - something went wrong", state_message)
                    self.send_error(500, None, state_message)
            else:
                self.send_error(411)
        else:
            self.send_error(415)
    except:
        print("uh oh")
        print(content_length, content_type, data)
        self.send_error(400)
    self.end_headers()
    return


def forbidden(self):
    self.send_error(403)
    self.end_headers()
    return


actions = {
    "/restart": restart_nautilus,
    "/terminate": terminate_server,
    "/config": save_config
}


class ActionsForNautilusRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        file_details = get_file_content(self.path)
        if "error" in file_details:
            self.send_error(file_details["error"], file_details.get(
                "message", "Unknown Error"))
            self.end_headers()
        else:
            self.send_response(200, "OK")
            self.send_header("Content-Type", file_details["mimetype"])
            self.end_headers()
            self.wfile.write(file_details["data"])

    def do_POST(self):
        return actions.get(self.path, forbidden)(self)


handler = ActionsForNautilusRequestHandler

PORT = int(sys.argv[1])
with http.server.ThreadingHTTPServer(("", PORT), handler) as httpd:
    print("localhost:" + str(httpd.server_address[1]))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
    print("terminating")

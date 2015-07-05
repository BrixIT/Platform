from platform_flask.models import db, AppInstance


class Nginx:
    proxies = {}

    def add_proxy(self, mountpoint, url):
        self.proxies[mountpoint] = url

    def load_instances(self):
        instances = AppInstance.query.order_by(AppInstance.mountpoint)
        for instance in instances:
            self.add_proxy(instance.mountpoint, "http://127.0.0.1:{}".format(instance.port))

    def generate_config(self):
        file = ["server {"]
        file.append("   listen 80 default_server;")
        file.append("   server_name _;")
        for mountpoint in self.proxies:
            file.append("   location /{} {{".format(mountpoint))
            file.append("       proxy_pass {}/{};".format(self.proxies[mountpoint], mountpoint))
            file.append("       proxy_pass_header Set-Cookie;")
            file.append("       proxy_hide_header Vary;")
            file.append("       proxy_set_header Accept-Encoding '';")
            file.append("       proxy_ignore_headers Cache-Control Expires;")
            file.append("       proxy_set_header Host $host;")
            file.append("   }")
        file.append("}")
        file_contents = "\n".join(file)
        return file_contents

    @classmethod
    def rebuild(cls):
        nginx = cls()
        nginx.load_instances()
        with open("/etc/nginx/sites-enabled/default", "w") as config_file:
            config_file.write(nginx.generate_config())

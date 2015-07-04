import configparser
import glob
import re
from subprocess import call, getoutput


class Systemd:
    def __init__(self):
        self.regex_unit_list = re.compile(
            r'(?P<name>[a-zA-Z0-9\.-]+)\.service\s+(?P<load>[a-z]+)\s+(?P<active>[a-z]+)\s+(?P<sub>[a-z]+)\s+(?P<description>.+)$',
            re.MULTILINE)

    def list(self):
        return [m for m in self.list_all() if m["name"].startswith("platform-")]

    def list_all(self):
        data = self.run_systemd_command("list-units --type=service")
        units_result = self.regex_unit_list.finditer(data)
        units = [m.groupdict() for m in units_result]
        return units

    def load(self, name):
        filename = "/etc/systemd/system/platform-{}.service".format(name)
        unit = SystemdUnit()
        unit.load_unit(filename)
        return unit

    def save(self, unit):
        if hasattr(unit, "name") and hasattr(unit, "save_unit"):
            name = "/etc/systemd/system/platform-{}.service".format(unit.name)
            unit.save_unit(name)
        else:
            raise Exception("{} is not a valid systemd unit object".format(type(unit)))

    def start(self, name):
        return call(["systemctl", "start", "platform-{}".format(name)])

    def stop(self, name):
        return call(["systemctl", "stop", "platform-{}".format(name)])

    def restart(self, name):
        return call(["systemctl", "restart", "platform-{}".format(name)])

    def run_systemd_command(self, command):
        return getoutput("systemctl {}".format(command))


class SystemdUnit:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.exec = ""
        self.environment = {}
        self.on_boot = False

    def save_unit(self, path):
        config = CaseSensitiveConfigParser()
        config["Unit"] = {
            "Description": self.description,
            "Requires": "nginx.service"
        }
        config["Service"] = {
            "ExecStart": self.exec,
            "Restart": "always",
            "StandardOutput": "journal",
            "StandardError": "journal",
            "SyslogIdentifier": self.name
        }
        config["Install"] = {
            "After": "nginx.service",
            "WantedBy": "multi-user.target"
        }
        if self.environment:
            environment = ""
            for key in self.environment:
                environment += "\"{}={}\" ".format(key, self.environment[key])
            config["Service"]["Environment"] = environment
        with open(path, "w") as target_file:
            config.write(target_file)

    def load_unit(self, path):
        config = CaseSensitiveConfigParser()
        config.read(path)
        self.exec = config["Service"]["ExecStart"]
        self.description = config["Unit"]["Description"]
        self.name = config["Service"]["SyslogIdentifier"]


class CaseSensitiveConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr

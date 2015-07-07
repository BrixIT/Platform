import configparser
import re
from subprocess import call, getoutput
import json
import datetime


class Systemd:
    def __init__(self):
        self.regex_unit_list = re.compile(
            r'(?P<name>[a-zA-Z0-9\.-]+)\.service\s+(?P<load>[a-z]+)\s+(?P<active>[a-z]+)\s+(?P<sub>[a-z]+)\s+(?P<description>.+)$',
            re.MULTILINE)

    def list(self):
        return [m for m in self.list_all() if m["name"].startswith("platform-")]

    def list_all(self):
        data = self.run_systemd_command("list-units --type=service --all")
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

    def command(self, command):
        call(['systemctl', command, 'platform-{}'.format(self.name)])

    def is_running(self):
        output = getoutput('systemctl is-active platform-{}'.format(self.name))
        return output == 'active'

    def save_unit(self, path):
        config = CaseSensitiveConfigParser()
        config["Unit"] = {
            "Description": self.description,
            "Requires": "nginx.service",
            "After": "nginx.service"
        }
        config["Service"] = {
            "ExecStart": self.exec,
            "Restart": "always",
            "StandardOutput": "journal",
            "StandardError": "journal",
            "SyslogIdentifier": self.name
        }
        config["Install"] = {
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

    def get_status(self):
        raw = getoutput('systemctl status platform-{}'.format(self.name))
        regex = re.compile(r'Active:\s+(?P<status>[a-z]+\s+\([a-z:\-\s]+\))')
        matches = regex.findall(raw)
        return {"status": matches[0]}

    def get_journal(self):
        raw = getoutput('journalctl -u platform-{} -o json'.format(self.name))
        if "Cannot assign requested address" in raw:
            return []
        for line in raw.split("\n"):
            log_line = json.loads(line)
            log_line['timestamp'] = datetime.datetime.fromtimestamp(int(log_line['__REALTIME_TIMESTAMP'][:-6]))
            yield log_line


class CaseSensitiveConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr

from platform_flask.components.configuration import PlatformConfig
from subprocess import call
from flask import render_template


class MailRelay:
    def build_config(self):
        smtp_config = PlatformConfig.get('smtp', {
            'host': '',
            'port': 25,
            'ssl': False,
            'auth': False,
            'username': '',
            'password': ''
        })
        relayhost = self._generate_postfix_relayhost(smtp_config)
        tls = 'yes' if smtp_config['ssl'] else 'no'
        postfix_config = render_template('main.cf', relayhost=relayhost, tls=tls)
        with open('/etc/postfix/main.cf', 'w') as postfix_configfile:
            postfix_configfile.write(postfix_config)
        call(['systemctl', 'reload', 'postfix'])

    def _generate_postfix_relayhost(self, smtp):
        if smtp['port'] == 25:
            return smtp['host']
        else:
            return '[{}]:{}'.format(smtp['host'], smtp['port'])

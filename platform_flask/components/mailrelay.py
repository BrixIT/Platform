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
        auth = 'yes' if smtp_config['auth'] else 'no'
        postfix_config = render_template('main.cf', relayhost=relayhost, tls=tls, auth=auth,
                                         use_auth=smtp_config['auth'])

        if smtp_config['auth']:
            with open('/etc/postfix/sasl_passwd', 'w') as password_file:
                password_file.write("{} {}:{}\n".format(relayhost, smtp_config['username'], smtp_config['password']))
            call(['postmap', '/etc/postfix/sasl_passwd'])

        with open('/etc/postfix/main.cf', 'w') as postfix_configfile:
            postfix_configfile.write(postfix_config)
        call(['systemctl', 'reload', 'postfix'])

    def _generate_postfix_relayhost(self, smtp):
        if smtp['port'] == 25:
            return smtp['host']
        else:
            return '[{}]:{}'.format(smtp['host'], smtp['port'])

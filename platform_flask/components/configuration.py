from platform_flask.models import db, Configuration
import json


class PlatformConfig:
    @staticmethod
    def get(key, default=None):
        query = Configuration.query.get(key)
        if not query:
            new_row = json.dumps({"value": default})
            new_entity = Configuration(key, new_row)
            db.session.add(new_entity)
            db.session.commit()
            return default
        else:
            return json.loads(query.value)['value']

    @staticmethod
    def set(key, value):
        row = json.dumps({"value": value})
        query = Configuration.query.get(key)
        if not query:
            query = Configuration(key, row)
        else:
            query.value = row
        db.session.add(query)
        db.session.commit()

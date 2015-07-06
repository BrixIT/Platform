import hashlib


def gravatar(email, size=100, rating='g', default='retro', force_default=False, use_ssl=False):
    if use_ssl:
        url = "https://secure.gravatar.com/avatar/"
    else:
        url = "http://www.gravatar.com/avatar/"
    email = email.encode('utf-8').strip()
    hashemail = hashlib.md5(email).hexdigest()
    link = "{url}{hashemail}?s={size}&d={default}&r={rating}".format(
        url=url, hashemail=hashemail, size=size,
        default=default, rating=rating)
    if force_default:
        link += "&f=y"
    return link

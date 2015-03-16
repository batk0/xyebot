import httplib2
from urllib import urlencode
import json
import sys


def set_token(token):
    Invoker.token = token


def get_token():
    return Invoker.token


class Invoker(object):
    prefix = ''
    token = ''
    def __init__(self):
        self.uri = 'https://slack.com/api/'
        self.http = httplib2.Http()

    def __wrap_method(self, params={}, http_method='GET'):
        return self.invoke(slack_method=self.name, params=params, http_method=http_method)

    def __getattribute__(self, name):
        try:
            return super(Invoker, self).__getattribute__(name)
        except:
            self.name = name
            return self.__wrap_method

    def invoke(self, slack_method, params={}, http_method='GET'):
        query = self.uri + self.prefix + '.' + slack_method
        post_data = None
        if self.token:
            params.update({'token':self.token})
        if params:
            if http_method == 'GET':
                query += '?' + urlencode(params)
            elif http_method == 'POST':
                post_data = json.dumps(params)
        try:
            (headers, content) = self.http.request(query, body = post_data, method=http_method)
            return json.loads(content)
        except:
            return sys.exc_info()

class Api(Invoker):
    prefix = 'api'
api = Api()


class Auth(Invoker):
    prefix = 'auth'
auth = Auth()


class Channels(Invoker):
    prefix = 'channels'
channels = Channels()


class Chat(Invoker):
    prefix = 'chat'
chat = Chat()


class Emoji(Invoker):
    prefix = 'emoji'
emoji = Emoji()


class Files(Invoker):
    prefix = 'files'
files = Files()


class Groups(Invoker):
    prefix = 'groups'
groups = Groups()


class Im(Invoker):
    prefix = 'im'
im = Im()


class Oauth(Invoker):
    prefix = 'oauth'
oauth = Oauth()


class RTM(Invoker):
    prefix = 'rtm'
rtm = RTM()


class Search(Invoker):
    prefix = 'search'
search = Search()


class Stars(Invoker):
    prefix = 'stars'
stars = Stars()


class Team(Invoker):
    prefix = 'team'
team = Team()


class Users(Invoker):
    prefix = 'users'
users = Users()


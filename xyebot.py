# -*- coding: utf-8 -*-
from bottle import Bottle,request
from threading import Timer
from random import randint
from time import time
from json import dumps
import xb_config as cfg
import slack_api as sa
import re


bottle = Bottle()
xb_run = False
oldest = time()
vow = u'аАеЕёЁиИоОуУыЫэЭюЮяЯ'
con = u'бБвВгГдДжЖзЗйЙкКлЛмМнНпПрРсСтТфФхХцЦчЧшШщЩъЪьЬ'
sv = {u'а':u'я',
    u'А':u'я',
    u'о':u'ё',
    u'О':u'ё',
    u'у':u'ю',
    u'У':u'ю',
    u'ы':u'и',
    u'Ы':u'и',
    u'э':u'е',
    u'Э':u'е'}


def process(msg):
    l = 0
    r = ''
    if msg['type'] == 'message':
        for word in msg['text'].split():
            w = re.match('['+vow+con+']{5,}$',word)
            if w: 
                if len(w.string) >= l:
                    l = len(w.string)
                    r = w.string
        if r:
            r = re.sub('^['+con+']*(.*)', u'\\1', r)
            if sv.has_key(r[0]):
                r = r.replace(r[0], sv[r[0]], 1)
            r = u'ху' + r
    return r


def __loop():
    global oldest
    for ch in cfg.channels.values():
        res = sa.channels.history({'channel':ch,'count':1, 'oldest':oldest, 'inclusive':1})
        if res['ok']:
            if res['messages']:
                text = process(res['messages'][0])
                if text and isinstance(text, unicode):
                    text = text.encode('utf8')
                    sa.chat.postMessage({'text':text, 'channel':ch, 'username':'xyebot'})
    oldest = time()
    if xb_run:
        Timer(randint(cfg.timeout_min, cfg.timeout_max), __loop).start()


@bottle.route('/oauth', method='GET')
def auth_error():
    print "Got error message %s" % request.params.get('error')
    return 'OK'


@bottle.route('/xyebot/start', method='GET')
def start():
    global xb_run
    global oldest
    if xb_run:
        return {'ok':False, 'xyebot':'start', 'message':'already started'}
    else:
        oldest = time()
        sa.set_token(cfg.token)
        for ch in cfg.channels.keys():
            res = sa.channels.join({'name':ch})
            if res['ok']:
                cfg.channels[ch] = res['channel']['id']
        xb_run = True
        Timer(randint(cfg.timeout_min, cfg.timeout_max), __loop).start()
        return {'ok':True, 'xyebot':'start'}


@bottle.route('/xyebot/stop', method='GET')
def stop():
    global xb_run
    if xb_run :
        sa.set_token('')
        xb_run = False
        return {'ok':True, 'xyebot':'stop'}
    else:
        return {'ok':True, 'xyebot':'stop', 'message':'already stopped'}

#@bottle.route('/xyebot/<ticker>', method='GET')
#def price(ticker):
#    pass
#  return { 'text': print_results(get_ticker(ticker)) }


# Define an handler for 404 errors.
@bottle.error(404)
def error_404(error):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.'


if __name__ == '__main__':
    print 'Starting XYEbot'
    bottle.run()

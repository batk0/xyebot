# -*- coding: utf-8 -*-
from threading import Timer, enumerate
from random import randint
from time import time
from json import dumps
import xb_config as cfg
import slack_api as sa
import re
import sys


sa.set_token(cfg.token)
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

    
def find_admin(name):
    res = sa.users.list()
    log("users.list: %s" % res)
    if res['ok']:
        for user in res['members']:
            if user['name'] == cfg.admin:
                return user['id']
    return None


def log(msg):
    if cfg.debug:
        print msg


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


def process_admin(ch_id, adm_id, msgs):
    if msgs:
        msg = msgs.pop() 
    else:
        return True
    r = ''
    try:
        if msg['type'] == 'message' and msg['user'] == adm_id and msg['text'].startswith(cfg.name):
            cmd = msg['text'].split()[1]
            if cmd == 'start':
                r = start()
            elif cmd == 'stop':
                r = stop()
            elif cmd == 'debug':
                cfg.debug = False if cfg.debug else True
                r = "Debug: %s" % cfg.debug
    except:
        r = "Exception: %s (%s)\n%s" % sys.exc_info()
    if r:
        log("chat.postMessage: %s" % sa.chat.postMessage({'text':r, 'channel':ch_id, 'username':cfg.name}))
    process_admin(ch_id, adm_id, msgs)


def __admin_loop(ch_id, adm_id, oldest):
    res = sa.im.history({'channel':ch_id, 'count':10, 'oldest':oldest, 'inclusive':0})
    log("im.history: %s" % res)
    if res['ok']:
        if res['messages']:
            process_admin(ch_id, adm_id, res['messages'])
    th = Timer(10, __admin_loop, [ch_id, adm_id, time()])
    th.setName('admin_loop')
    th.start()
    

def __loop(oldest):
    for ch in cfg.channels.values():
        res = sa.channels.history({'channel':ch, 'count':100, 'oldest':oldest, 'inclusive':0})
        log("channels.history: %s" % res)
        if res['ok']:
            if res['messages']:
                text = process(res['messages'][0])
                log("message: %s" % text)
                if text and isinstance(text, unicode):
                    text = text.encode('utf8')
                res = sa.chat.postMessage({'text':text, 'channel':ch, 'username':cfg.name})
                log("chat.postMessage: %s" % res)
    if cfg.run:
        th = Timer(randint(cfg.timeout_min, cfg.timeout_max), __loop, [time()])
        th.setName('loop')
        th.start()


def start():
    if cfg.run:
        return {'ok':False, 'xyebot':'start', 'message':'already started'}
    else:
        for ch in cfg.channels.keys():
            res = sa.channels.join({'name':ch})
            log("channel.join: %s" % res)
            if res['ok']:
                cfg.channels[ch] = res['channel']['id']
        cfg.run = True
        __loop(time())
        return {'ok':True, 'xyebot':'start'}


def stop():
    if cfg.run:
        for th in enumerate():
            if th.getName() == 'loop':
                th.cancel()
        cfg.run = False
        return {'ok':True, 'xyebot':'stop'}
    else:
        return {'ok':True, 'xyebot':'stop', 'message':'already stopped'}


if __name__ == '__main__':
    log('Starting XYEbot')
    admin_id = find_admin(cfg.admin)
    if admin_id:
        res = sa.im.open({'user':admin_id})
        log("im.open: %s" % res)
        if res['ok']:
            __admin_loop(res['channel']['id'], admin_id, time())

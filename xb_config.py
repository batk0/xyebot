from random import choice
import string

def __id_generator(size=12, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
  return ''.join(choice(chars) for _ in range(size))

# Authorization config
oauth_uri = 'https://slack.com/oauth/authorize'
# Your token or token of standalone bot
token = ''
# Standalone bot config
client_id = ''
team = ''
state = __id_generator()
# Common options
channels = {'general':''}
timeout_min = 50
timeout_max = 100

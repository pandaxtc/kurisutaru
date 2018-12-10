import asyncio
import re
import random

import plugins

import logging

logger = logging.getLogger()

BAD_WORDS = []

last_word = ''

dir = '/home/waylon/hangoutsbot/hangupsbot/plugins/bad_words.txt'


def _initialise(bot):
    load()
    plugins.register_handler(_handle_bad_words, type = 'message')
    plugins.register_handler(_handle_bad_names, type = 'rename')
    plugins.register_handler(_handle_toxicity, type = 'message')
    plugins.register_user_command(['language', 'lastword', 'analyze'])
    plugins.register_admin_command(['langadd', 'langdel', 'langload'])
    plugins.register_user_command(['koby'])


def _handle_bad_names(bot, event, command):
    if langcheck(str.lower(event.text)):
        yield from command.run(bot, event, 'language')
        yield from command.run(bot, event, *["convrename", "id:" + event.conv_id, event.conv_event.old_name])
        logger.info("[Language] Bad word detected in name!")


def _handle_bad_words(bot, event, command): #handler to detect bad words
    if langcheck(event.text):
        yield from command.run(bot, event, 'language')
        logger.info("[Language] Bad word detected in message!")


def language(bot, event):
    if random.random() < 0.1:
        yield from bot.coro_send_message(event.conv, 'D-don\'t say those naughty words, baka!')
    else:
        yield from bot.coro_send_message(event.conv, 'Language!') #send message

#langadd and langdel modify the file, then reload it. this is probably inefficient, but whatever.

def langadd(bot, event, *args): #adds a word to the bad_words.txt file and the BAD_WORDS list
    logger.info("[Language] Adding " + ', '.join(args) + " to language list!")
    with open(dir, 'a') as file:
        for word in args:
            file.write(word + '\n')
    load()
    yield from bot.coro_send_message(event.conv, 'Added ' + ', '.join(args) + ' to language list!')


def langdel(bot, event, *args):
    logger.info('[Language] Removing ' + ', '.join(args) + ' from language list!')
    with open(dir, 'r') as file:
        data = file.readlines()
    data = list(filter(lambda x: not (x.strip() in args), data)) #replace data with an array with all *args filtered out
    with open(dir, 'w') as file:
        file.write(''.join(data))
    load()
    yield from bot.coro_send_message(event.conv, 'Removed ' + ', '.join(args) + ' from language list!')


def load(): #reloads bad_words.txt into BAD_WORDS
    logger.info("[Language] Reloading language list!")
    global BAD_WORDS
    with open(dir, 'r') as f:
        BAD_WORDS = f.readlines()
        BAD_WORDS = list(map(lambda x: x.strip(), BAD_WORDS))
        logger.info('[Language] Loaded new file! CONTENTS: ' + ', '.join(BAD_WORDS))

def langload(bot, event):
    load()
    yield from bot.coro_send_message(event.conv, 'Reloaded language list!')


def langcheck(text):
    text = text.lower()
    global last_word
    for s in BAD_WORDS:
        if re.search(r"\s{0}|{0}\s|^{0}".format(s), text) is not None:
            last_word = s
            return True
    return False

def findwords(s):
    s = s.lower()
    return (w for w in BAD_WORDS if s.find(w) != -1)


def lastword(bot, event):
    if last_word != '':
        yield from bot.coro_send_message(event.conv, 'Last detected word: ' + last_word)
    else:
        yield from bot.coro_send_message(event.conv, 'No words detected so far! Ara ara~!')


def analyze(bot, event, *args):
    yield from bot.coro_send_message(event.conv, 'Bad words detected in string: {}'.format(', '.join(findwords(' '.join(args)))))

TOXIC = [
    'apply',
    '\\bsat\\b',
    '\\bpsat\\b',
    '\\bact\\b',
    'college',
    'university',
    'application',
    'early action',
    'early decision',
    '\\buc\\b',
    'admit',
    'admission',
    '\\brec\\b',
    'recommendation',
]

def _handle_toxicity(bot, event, command):
    if any(map(lambda word: re.search(word, event.text.lower()) is not None, TOXIC)) and random.random() < 0.1:
        yield from bot.coro_send_message(event.conv, 'TOXIC')

koby_hw = ''

def koby(bot, event, *args):
    global koby_hw
    if len(args) > 0 and args[0].lower() == 'set':
        koby_hw = ' '.join(args[1:])
        yield from bot.coro_send_message(event.conv, 'Ty ill do it later')
    else:
        yield from bot.coro_send_message(event.conv, 'Hai, hai, the koby hw is {} but i havent done it yet'.format(koby_hw))

import asyncio, logging, re, string

import plugins
from .mentions import mention

from utils import remove_accents


logger = logging.getLogger(__name__)


def _initialise(bot):
    _init_memory(bot)
    plugins.register_user_command(['group_join', 'group_leave', 'groups', 'my_groups', 'in_group'])
    plugins.register_admin_command(['group_mention'])


def _init_memory(bot):
    if not bot.memory.exists(['groups']):
        bot.memory.set_by_path(['groups'], {})

def _clean(s):
    return ''.join(e for e in remove_accents(s).lower() if e.isalnum() or e in ['-'])


def group_join(bot, event, *args):
    groups = map(_clean, args)
    uid = event.user.id_.chat_id

    joined = []
    already_in = []

    if not bot.memory.exists(['user_data', uid, 'groups']):
        bot.memory.set_by_path(['user_data', uid, 'groups'], [])

    for group in groups:
        if not bot.memory.exists(['groups', group]):
            bot.memory.set_by_path(['groups', group], {})
            bot.memory.set_by_path(['groups', group, 'members'], [])
        members = bot.memory.get_by_path(['groups', group, 'members'])
        if uid in members:
            logger.info('{} already in group {}'.format(uid, group))
            already_in.append(group)
        else:
            members.append(uid)
            bot.user_memory_get(uid, 'groups').append(group)
            logger.info('{} joined group {}'.format(uid, group))
            joined.append(group)

    yield from bot.coro_send_message(event.conv, 'Joined groups {}; Already in groups {}'
                                     .format(', '.join(joined), ', '.join(already_in)))


def group_leave(bot, event, *args):
    groups = map(_clean, args)
    uid = event.user.id_.chat_id

    left = []
    not_in = []

    for group in groups:
        if bot.memory.exists(['groups', group]):
            members = bot.memory.get_by_path(['groups', group, 'members'])
            if uid in members:
                members.remove(uid)
                bot.user_memory_get(uid, 'groups').remove(group)
                logger.info('{} left group {}'.format(uid, group))
                left.append(group)

                if not members:
                    logger.info('Nobody left in group {}, removing'.format(group))
                    bot.memory.pop_by_path(['groups', group])
            else:
                logger.info('{} not already in group {}'.format(uid, group))
                not_in.append(group)
        else:
            not_in.append(group)

    yield from bot.coro_send_message(event.conv, 'Left groups {}; Not in groups {}'
                                     .format(', '.join(left), ', '.join(not_in)))


def groups(bot, event, *args):
    yield from bot.coro_send_message(event.conv, 'Groups:<br />{}'.format('<br />'.join(group for group in bot.memory.get_by_path(['groups']))))


def my_groups(bot, event, *args):
    uid = event.user.id_.chat_id

    if bot.memory.exists(['user_data', uid, 'groups']):
        groups = bot.memory.get_by_path(['user_data', uid, 'groups'])
    else:
        groups = []

    yield from bot.coro_send_message(event.conv, 'Rooms you are in: {}'.format(', '.join(groups)))


def in_group(bot, event, group):
    group = _clean(group)
    members = bot.memory.get_by_path(['groups', group, 'members'])
    names = [bot.memory.get_by_path(['user_data', member, '_hangups', 'full_name']) for member in members]

    yield from bot.coro_send_message(event.conv, 'Members of group {}:<br />{}'.format(group, '<br />'.join(names)))

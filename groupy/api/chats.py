from . import base
from . import messages
from groupy import pagers


class Chats(base.Manager):
    """A chat manager."""

    def __init__(self, session):
        super().__init__(session, 'chats')

    def _raw_list(self, **params):
        """List all chats.

        :param args params: listing paramters
        :return: chats with other users
        :rtype: :class:`~groupy.pagers.ChatList`
        """
        response = self.session.get(self.url, params=params)
        return [Chat(self, **chat) for chat in response.data]

    def list(self, page=1, per_page=10):
        """List all chats.

        :param int page: which page
        :param int per_page: how many chats per page
        :return: chats with other users
        :rtype: :class:`~groupy.pagers.ChatList`
        """
        return pagers.ChatList(self, self._raw_list, per_page=per_page,
                               page=page)


class Chat(base.ManagedResource):
    """A chat with another user."""

    def __init__(self, manager, **data):
        super().__init__(manager, **data)
        self.messages = messages.DirectMessages(self.manager.session,
                                                self.other_user['id'])

    def __repr__(self):
        klass = self.__class__.__name__
        return '<{}(other_user={!r})>'.format(klass, self.other_user['name'])

    def post(self, text=None, attachments=None):
        """Post a message to the chat.

        :param str text: the text of the message
        :param attachments: a list of attachments
        :type attachments: :class:`list`
        :return: ``True`` if successful
        :rtype: bool
        """
        return self.messages.create(text=text, attachments=attachments)
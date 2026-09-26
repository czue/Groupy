import unittest

from groupy.api import attachments


class TestAttachmentsFromData(unittest.TestCase):
    def test_known_attachment_type(self):
        data = {'type': 'split', 'token': 'foo'}
        attachment = attachments.Attachment.from_data(**data)
        self.assertIsInstance(attachment, attachments.Split)

    def test_unknown_attachment_type(self):
        data = {'type': 'foo', 'bar': 'baz'}
        attachment = attachments.Attachment.from_data(**data)
        self.assertIsInstance(attachment, attachments.Attachment)

    def test_known_attachment_type_with_unknown_field(self):
        data = {'type': 'split', 'token': 'foo', 'unknown': 'field'}
        attachment = attachments.Attachment.from_data(**data)
        self.assertIsInstance(attachment, attachments.Split)
        self.assertEqual(attachment.to_json(), data)

    def test_mentions_with_unknown_field(self):
        data = {'type': 'mentions', 'loci': [[0, 4]], 'user_ids': ['1'],
                'replay_allowed': True}
        attachment = attachments.Attachment.from_data(**data)
        self.assertIsInstance(attachment, attachments.Mentions)
        self.assertEqual(attachment.data['user_ids'], ['1'])
        self.assertEqual(attachment.data['replay_allowed'], True)

    def test_known_attachment_type_missing_required_field(self):
        data = {'type': 'split', 'unknown': 'field'}
        attachment = attachments.Attachment.from_data(**data)
        self.assertIs(type(attachment), attachments.Attachment)
        self.assertEqual(attachment.to_json(), data)

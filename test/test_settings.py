from unittest import TestCase
from unittest.mock import patch

import gist
import helpers
from test.stubs import sublime
from test.stubs import github_api

DEFAULT_GISTS_URL = 'https://api.github.com/gists?per_page=100'
DEFAULT_USER_GISTS_URL = 'https://api.github.com/users/%s/gists?per_page=100'
DEFAULT_STARRED_GISTS_URL = 'https://api.github.com/gists/starred?per_page=100'
DEFAULT_ORGS_URL = 'https://api.github.com/user/orgs'

CUSTOM_API_URL = 'https://github.domain.test/api/v3'
CUSTOM_GISTS_URL = 'https://github.domain.test/api/v3/gists?per_page=80'
CUSTOM_USER_GISTS_URL = 'https://github.domain.test/api/v3/users/%s/gists?per_page=80'
CUSTOM_STARRED_GISTS_URL = 'https://github.domain.test/api/v3/gists/starred?per_page=80'
CUSTOM_ORGS_URL = 'https://github.domain.test/api/v3/user/orgs'


class TestGistSettings(TestCase):
    def setUp(self):
        gist.plugin_loaded()

    def tearDown(self):
        gist.settings = None
        sublime.settings_storage = {}

    def test_settings_reload(self):
        sublime._reload_settings('Gist.sublime-settings')
        self.assertEqual(gist.settings.get('GISTS_URL'), DEFAULT_GISTS_URL)
        self.assertEqual(gist.settings.get('USER_GISTS_URL'), DEFAULT_USER_GISTS_URL)
        self.assertEqual(gist.settings.get('STARRED_GISTS_URL'), DEFAULT_STARRED_GISTS_URL)
        self.assertEqual(gist.settings.get('ORGS_URL'), DEFAULT_ORGS_URL)

    def test_custom_url_setting(self):
        gist.settings.set('api_url', CUSTOM_API_URL)
        gist.settings.set('max_gists', 80)
        gist.set_settings()
        self.assertEqual(gist.settings.get('GISTS_URL'), CUSTOM_GISTS_URL)
        self.assertEqual(gist.settings.get('USER_GISTS_URL'), CUSTOM_USER_GISTS_URL)
        self.assertEqual(gist.settings.get('STARRED_GISTS_URL'), CUSTOM_STARRED_GISTS_URL)
        self.assertEqual(gist.settings.get('ORGS_URL'), CUSTOM_ORGS_URL)

    @patch('gist.sublime.status_message')
    def test_max_gists(self, patched_status_message):
        gist.settings.set('max_gists', 101)
        gist.set_settings()
        self.assertEqual(gist.settings.get('max_gists'), 100)
        patched_status_message.assert_called_with('Gist: GitHub API does not support a value of higher than 100')

        gist.settings.set('max_gists', 42)
        gist.set_settings()
        self.assertEqual(gist.settings.get('max_gists'), 42)

    def test_prefer_filename(self):
        settings = sublime.load_settings('Gist.sublime-settings')
        settings.set('show_authors', False)

        # prefer_filename = False and with description - prefer description
        settings.set('prefer_filename', False)
        result = helpers.gist_title(github_api.GIST_WITH_DESCRIPTION)
        self.assertEqual(result, ['some description'])

        # prefer_filename = True and with description - prefer one of file names
        settings.set('prefer_filename', True)
        result = helpers.gist_title(github_api.GIST_WITH_DESCRIPTION)
        self.assertIn(result, (['some_file.txt'], ['another_file.cpp']))

        # prefer_filename = True and without description - prefer one of file names
        settings.set('prefer_filename', False)
        result = helpers.gist_title(github_api.GIST_WITHOUT_DESCRIPTION)
        self.assertIn(result, (['some_file.txt'], ['another_file.cpp']))

        # prefer_filename = False and without description - still prefer one of file names
        settings.set('prefer_filename', True)
        result = helpers.gist_title(github_api.GIST_WITHOUT_DESCRIPTION)
        self.assertIn(result, (['some_file.txt'], ['another_file.cpp']))

    def test_show_authors(self):
        settings = sublime.load_settings('Gist.sublime-settings')
        settings.set('prefer_filename', False)

        settings.set('show_authors', False)
        result = helpers.gist_title(github_api.GIST_WITH_DESCRIPTION)
        self.assertEqual(result, ['some description'])

        settings.set('show_authors', True)
        result = helpers.gist_title(github_api.GIST_WITH_DESCRIPTION)
        self.assertEqual(result, ['some description', 'some_user'])


    # TODO: test: supress_save_dialog, update_on_save (see test_open_gist)
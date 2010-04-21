# -*- coding: utf-8 -*-
# Moovida - Home multimedia server
# Copyright (C) 2006-2009 Fluendo Embedded S.L. (www.fluendo.com).
# All rights reserved.
#
# This file is available under one of two license agreements.
#
# This file is licensed under the GPL version 3.
# See "LICENSE.GPL" in the root of this distribution including a special
# exception to use Moovida with Fluendo's plugins.
#
# The GPL part of Moovida is also available under a commercial licensing
# agreement from Fluendo.
# See "LICENSE.Moovida" in the root directory of this distribution package
# for details on that license.
#
# Author: Adam Svanberg <asvanberg@gmail.com>


from elisa.core.utils import defer
from elisa.core.utils.i18n import install_translation
from elisa.core.common import application

from elisa.plugins.poblesec.base.preview_list import *
from elisa.plugins.poblesec.base.list import GenericListViewMode, BaseListController
from elisa.plugins.poblesec.music_library import TracksViewMode
from elisa.plugins.poblesec.link import Link, LinksMenuController

from elisa.plugins.poblesec.plugins_settings import GenericSettingsController
from elisa.plugins.poblesec.login import LoginController

from elisa.plugins.spotify.utils import get_spotify_provider, spotify_error_message
from elisa.plugins.spotify.actions import *

_ = install_translation('spotify')
_poblesec = install_translation('poblesec')

#
# Main spotify interface
#

def spotify_decorator(controller):
    """
    Adds a link to the main controller of the Spotify plugin.
    """
    link = Link(controller_path='/poblesec/spotify/main', label=_('Spotify'))
    controller.model.append(link)

    return defer.succeed(None)


class SpotifyMainController(LinksMenuController, MenuItemPreviewListController):
    """
    Main controller of the example plugin defining its main menu.

    It's a LinksMenuController that is displaying a list of links, and a
    MenuItemPreviewListController that is a visually vertical one.
    """

    item_widget_kwargs = {'with_artwork_box': False}

    def populate_model(self):

        link_playlists = Link(
            controller_path='/poblesec/spotify/playlists', 
            label=_('Playlists')
        )

        link_search = Link(
            controller_path='/poblesec/spotify/search',
            label=_('Search')
        )

        return defer.succeed([link_playlists, link_search])




class SpotifyPlaylistViewMode(GenericListViewMode):
    """
    Defines how list items are rendered
    """
    def get_label(self, item):
        return defer.succeed(item.title)

    def get_default_image(self, item):
        return None

    def get_image(self, item, theme):
        return defer.succeed(None)


class SpotifyPlaylistsController(MenuItemPreviewListController):
    """
    Controller displaying the user's spotify playlists.
    """

    view_mode = SpotifyPlaylistViewMode
    item_widget_kwargs = {'with_artwork_box': False}
    empty_label = _('There are no playlists in this section')

    uri = 'spotify://playlists'

    def populate_model(self):
        return application.resource_manager.get(self.uri)

    def create_actions(self):
        return SpotifyPlaylistAction(self), []


class SpotifyTracksViewMode(TracksViewMode):
    """
    Defines how list items are rendered
    """

    def get_sublabel(self, item):
        return defer.succeed(','.join([str(a) for a in item.artists]))



class SpotifyPlaylistTracksController(DoubleLineMenuItemPreviewListController):
    """
    Controller displaying tracks in a playlist
    """

    view_mode = SpotifyTracksViewMode
    item_widget_kwargs = {'with_artwork_box': False}
    empty_label = _('There are no tracks in this playlist')

    uri = 'spotify://playlist'

    def initialize(self, item):
        self.playlist_model = item
        return super(SpotifyPlaylistTracksController, self).initialize()

    def populate_model(self):
        return defer.succeed(self.playlist_model)
        
    def create_actions(self):
        return SpotifyTrackAction(self), []







#
# Settings
#

def spotify_settings_decorator(controller):
    controller.append_plugin('spotify', _('Spotify'), '/poblesec/spotify/settings')
    return defer.succeed(None)


class SpotifySettingsController(GenericSettingsController):

    def populate_model(self):
        action = AuthenticationAction(self)
        action.connect('name-changed', self._action_name_changed_cb)
        model = [action,]
        return defer.succeed(model)

    def _action_name_changed_cb(self, *args):
        self.refresh()


class SpotifyLoginController(LoginController):

    
    def login(self, username, password):
        # Overridden from mother class.
        try:
            provider = get_spotify_provider()
        except ResourceProviderNotFound, error:
            return defer.fail(error)
        else:
            return provider.login(username, password)

    def success(self, result):
        # Overridden from mother class.
        browser = self.frontend.retrieve_controllers('/poblesec/browser')[0]
        paths = [('/poblesec/internet_menu', _poblesec('INTERNET MEDIA'), {}),
                 ('/poblesec/music/internet', _poblesec('Music'), {}),
                 ('/poblesec/spotify/main', _('Spotify'), {})]
        return browser.navigate(paths)

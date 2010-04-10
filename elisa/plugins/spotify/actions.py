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


from elisa.core.utils.i18n import install_translation
from elisa.plugins.poblesec.actions import Action, LinkAction
from elisa.core.action import ContextualAction
from elisa.plugins.spotify.utils import get_spotify_provider, stop_animation_on_error

_ = install_translation('spotify')

class AuthenticationAction(ContextualAction):

    def __init__(self, controller):
        super(AuthenticationAction, self).__init__(controller)
        provider = get_spotify_provider()
        if provider.is_logged_in():
            self.name = _("Log out")
        else:
            self.name = _("Log in")

    def execute(self, item):
        provider = get_spotify_provider()
        if provider.is_logged_in():
            self.name = _("Log in")
            provider.logout()
            dfr = defer.succeed(None)
        else:
            def controller_appended(result):
                self.name = _("Log out")
                return result

            browser = self.controller.frontend.retrieve_controllers('/poblesec/browser')[0]
            path = "/poblesec/spotify/login"
            title = _("Log in")
            dfr = browser.history.append_controller(path, title)
            dfr.addCallback(controller_appended)
        return dfr

class LoginAction(LinkAction):
    """ L{LinkAction} leading to the Spotify login form.
    """

    title = _('Login to Spotify')
    path = '/poblesec/spotify/login'



class LogoutAction(Action):
    """ Action used to clear the Spotify resource_provider
    authentication token and go back to the previous menu. This action
    is called from the 'My Account' menu.
    """

    title = _('Logout From Spotify')

    def run(self):
        get_spotify_provider().logout()

        frontend = self.controller.frontend
        browser = frontend.retrieve_controllers('/poblesec/browser')[0]
        return browser.history.go_back()


class SpotifyPlaylistAction(ContextualAction):
    """ 
    L{LinkAction} leading to a Spotify playlist.
    """

    def execute(self, item):
        browser = self.controller.frontend.retrieve_controllers('/poblesec/browser')[0]
        path = '/poblesec/spotify/playlist'
        dfr = browser.history.append_controller(
            path, 
            item.name, 
            track_uris=item.track_uris
        )
        dfr.addErrback(stop_animation_on_error, self.controller)
        return dfr

class SpotifyTrackAction(ContextualAction):
    """ 
    L{LinkAction} leading to a Spotify track.
    """

    def execute(self, item):
        browser = self.controller.frontend.retrieve_controllers('/poblesec/browser')[0]
        path = '/poblesec/spotify/track'
        dfr = browser.history.append_controller(
            path, 
            item.name, 
            track_uris=item.track_uris
        )
        dfr.addErrback(stop_animation_on_error, self.controller)
        return dfr




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

import os
import re
import time

from elisa.core.utils import defer
from elisa.core.utils.i18n import install_translation
from elisa.core.components.resource_provider import ResourceProvider

from elisa.plugins.spotify.models import *
from elisa.plugins.spotify.spotifyclient import SpotifyClient
from elisa.plugins.spotify import pyspotify
from twisted.internet import threads
from elisa.core.log import Loggable

_ = install_translation('spotify')

class SpotifyResourceProvider(ResourceProvider):
    """
    Manages the pyspotify session
    """
    supported_uri = 'spotify://.*'

    default_config = {'username': '', 'password': ''}

    def __init__(self, *args, **kwargs):
        Loggable.__init__(self, *args, **kwargs)
        super(SpotifyResourceProvider, self).__init__(*args, **kwargs)
        self.debug("spotify resource privoder is now initialized")
    
    def initialize(self):
        self.client = None
        username = self.config['username'] or None
        password = self.config['password'] or None
        if username and password:
            self.debug("logging in from initialize")
            self.login(username, password)
        dfr = super(SpotifyResourceProvider, self).initialize()
        return dfr

    def login(self, username, password):
        """Log in by creating and starting a new spotify client"""

        def start_client():
            self.client = SpotifyClient(username, password)
            self.client.start()
            return self.client.login_dfr

        if self.client:
            dfr = self.logout()
            dfr.addCallback(start_client)
            return dfr
        else:
            return start_client()
    
    def logout(self):
        """Disconnect the client and return a deferred fired on logout"""
        self.client.disconnect()
        self.client = None
        return self.client.logout_dfr

    def is_logged_in(self):
        return self.client is not None

    def clean(self):
        """Makes sure we disconnect properly before shutdown"""
        self.debug("Running spotify resource provider clean method")
        self.client.disconnect()
        dfr = self.client.logout_dfr
        dfr.addCallback(lambda r: super(SpotifyResourceProvider, self).clean())
        return dfr


    def get_playlists(self):
        """
        Return playlists as model instances.
        
        Probably no need to defer, since the playlists are initialized
        on login.
        """
        playlists = []
        for playlist in self.client.playlists:
            model = SpotifyPlaylistModel()
            model.name=playlist.name()
            model.uri=pyspotify.Link.from_playlist(playlist)
            model.track_uris=[pyspotify.Link.from_track(track, 0) for track in playlist]
            playlists.append(model)
        return playlists


    def get_playlist_tracks(self, track_uris):
        tracks = []
        for track_uri in track_uris:
            track = track_uri.as_track()
            model = SpotifyTrackModel()
            model.name=track.name()
            model.artists=track.artists()
            model.album=track.album()
            model.uri=track_uri 
            tracks.append(model)
        return tracks
        
        
    def get(self, uri, context_model=None):
        """Handle spotify:// URIs"""
        if uri == 'spotify://playlists':
            return threads.deferToThread(self.get_playlists)

    def post(self, uri, **kwargs):
        """Handle spotify:// URIs"""
        if uri == 'spotify://playlist':
            track_uris = kwargs['track_uris']
            return threads.deferToThread(self.get_playlist_tracks, track_uris)

    


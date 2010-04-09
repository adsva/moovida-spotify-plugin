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

_ = install_translation('spotify')

class SpotifyResourceProvider(ResourceProvider):
    """
    Manages the pyspotify session
    """
    supported_uri = 'spotify://.*'

    def initialize(self):
        dfr = super(SpotifyResourceProvider, self).initialize()
        self.client = None
        return dfr

    def login(self, username, password):
        """Log in by creating and starting a new spotify client"""
        self.client = SpotifyClient(username, password)
        self.client.start()
        return self.client.login_dfr
    
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
            model.uri=pyspotify.Link().from_playlist(playlist)
            model.num_songs=len(playlist)
            playlists.append(model)
        return playlists
        
    def get(self, uri, context_model=None):
        """Handle spotify:// URIs"""

        if uri == 'spotify://playlists':
            return self.get_playlists()

    


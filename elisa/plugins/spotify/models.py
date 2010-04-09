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

from elisa.core import common

from elisa.core.components.model import Model

from elisa.plugins.base.models.audio import ArtistModel, AlbumModel, TrackModel

from elisa.core.media_uri import MediaUri

from elisa.core.utils import defer

from elisa.plugins.http_client.http_client import ElisaAdvancedHttpClient
from twisted.web2 import responsecode

from elisa.core.utils.i18n import install_translation

_ = install_translation('spotify')
_poblesec = install_translation('poblesec')


class SpotifyPlaylistModel(Model):

    def __init__(self):
        super(SpotifyPlaylistModel, self).__init__()
        self.name = None
        self.uri = None
        self.num_songs = None
        


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
from elisa.core.utils.i18n import install_translation
from elisa.plugins.poblesec import modal_popup

_ = install_translation('spotify')
_poblesec = install_translation('poblesec')


def get_spotify_provider():
    """ 
    Utility to find Spotify resource_provider instance in 
    the resource_manager.

    @rtype: L{elisa.core.components.resource_provider.ResourceProvider}
    """

    provider_path = 'elisa.plugins.spotify.resource_provider:SpotifyResourceProvider'
    manager = common.application.resource_manager
    provider = manager.get_resource_provider_by_path(provider_path)

    return provider


def spotify_error_message(result, controller=None):
    """
    Function for popping up an error message in case of problems communicating
    with spotify.
    """

    frontend = common.application.interface_controller.frontends.values()[0]
    main = frontend.retrieve_controllers('/poblesec')[0]
    icon = 'elisa.plugins.poblesec.warning'
    title = _('Error response from Spotify')

    text = '%s' % result.value.message

    buttons = [(_poblesec('Close'), main.hide_popup)]

    main.enqueue_popup(icon, title, text, buttons, modal_popup.ErrorPopup)

    return result


def stop_animation_on_error(failure, controller):
    """
    Function for stopping animation next to the menu item in case of some failure.
    """
    controller.stop_loading_animation()

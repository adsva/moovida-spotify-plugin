# -*- coding: utf-8 -*-
# Author: Adam Svanberg <asvanberg@gmail.com>

"""
setuptools script for the plugin.
"""

import os
from setuptools import setup, find_packages, Extension
from elisa.core.utils.dist import find_packages, TrialTest, Clean

packages, package_dir = find_packages(os.path.dirname(__file__))
cmdclass = dict(test=TrialTest, clean=Clean)

setup(
    name='elisa-plugin-spotify',
    version='0.1',
    description='Spotify',
    long_description='Spotify streaming music service, premium account required.',
    license='GPL3',
    author='Adam Svanberg',
    author_email='asvanberg@gmail.com',
    namespace_packages=['elisa', 'elisa.plugins', 'elisa.plugins.spotify','elisa.plugins.spotify.pyspotify'],
    packages=packages,
    package_dir=package_dir,
    cmdclass=cmdclass,
    decorator_mappings=[
        ('/poblesec/music/internet', 
         'elisa.plugins.spotify.controllers:spotify_decorator'),
        ('/poblesec/settings/plugins', 
         'elisa.plugins.spotify.controllers:spotify_settings_decorator'),
        ],
    controller_mappings=[
        ('/poblesec/spotify/main', 
         'elisa.plugins.spotify.controllers:SpotifyMainController'),
        ('/poblesec/spotify/playlists', 
         'elisa.plugins.spotify.controllers:SpotifyPlaylistsController'),
        ('/poblesec/spotify/playlist', 
         'elisa.plugins.spotify.controllers:SpotifyPlaylistTracksController'),
        ('/poblesec/spotify/search', 
         'elisa.plugins.spotify.controllers:SpotifySearchController'),
        
        ('/poblesec/spotify/settings',
         'elisa.plugins.spotify.controllers:SpotifySettingsController'),
        ('/poblesec/spotify/login',
         'elisa.plugins.spotify.controllers:SpotifyLoginController'),
        ],
    entry_points="""\
    [elisa.core.components.resource_provider]
    SpotifyResourceProvider = elisa.plugins.spotify.resource_provider:SpotifyResourceProvider
    """,
    package_data={
        '': ['*.png', '*.conf', '*.pyd', '*.so'],
        },
    data_files = [
        ('elisa/plugins/spotify/icons', 
         ['elisa/plugins/spotify/icons/icon1.png',
          'elisa/plugins/spotify/icons/icon2.png']),
    ],
    eager_resources = [
        'elisa/plugins/spotify/pyspotify/libspotify.so',
    ],
    zip_safe=True,
)

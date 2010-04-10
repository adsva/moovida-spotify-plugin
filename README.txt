==============
Spotify Plugin
==============

This moovida plugin uses Doug Winter's pyspotify library
(http://github.com/winjer/pyspotify), slightly modified by me to make
it easier to bundle with the plugin instead of making the user intall
the library separately. My spotify app-key is compiled into
_spotify.so, so the library only needs a valid username and password.


Running the Plugin
##################

Simplest installation procedure:

$ python setup.py bdist_egg
$ cp dist/elisa_plugin_spotify-0.1-py2.6.egg ~/.moovida/plugins/

To avoid manually logging in every time, put your spotify credentials
in ~/.moovida/moovida.conf

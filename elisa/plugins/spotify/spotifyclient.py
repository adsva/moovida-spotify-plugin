import sys
import os
import time
import pyspotify as spotify
import threading
from twisted.internet import reactor, defer, error
from elisa.core.log import Loggable

class SpotifyClient(threading.Thread, Loggable):
    """Handles api calls to and callbacks from the spotify subsystem"""

    api_version = spotify.api_version
    cache_location = 'tmp'
    settings_location = 'tmp'
    user_agent = 'moovida-spotify-plugin'


    def __init__(self, username, password, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        Loggable.__init__(self, *args, **kwargs)

        self.username = username
        self.password = password
        self.finished = False
        self.awoken = threading.Event()

        self.playlists = []
        self.song_queue = []
        self.session = None

        self.connected = False
        self.login_failed = False
        self.playing = False

        # Deferreds
        self.login_dfr = defer.Deferred()
        self.logout_dfr = defer.Deferred()


    def run(self):
        self.connect()
        self.debug('Spotify client thread terminating')

    def connect(self):
        self.debug('Connecting to spotify')
        self.session = spotify.connect(self)
        self.loop() 

    def loop(self):
        """ The main loop. This processes events and then either waits for an
        event. The event is either triggered by a timer expiring, or by a
        notification from within the spotify subsystem (it calls the wake
        method below). """
        self.debug('Entering spotify main loop')
        while not self.finished:
            self.awoken.clear()
            timeout = self.session.process_events()
            self.awoken.wait(timeout/1000.0)
        self.debug('Exiting spotify main loop')
        self.logout_dfr.callback(True)

    def disconnect(self):
        self.debug('Disconnecting from spotify')
        self.session.logout()


    # Spotify callbacks
        
    def wake(self, session):
        """ Called by the spotify subsystem to wake up the main loop. """
        self.awoken.set()

    def logged_in(self, session, error):
        """Called after attempted login"""
        if error:
            self.debug('Login to spotify failed: %s' % error)
            self.login_dfr.errback()
        else:
            self.debug('Connected to spotify')
            self.playlists = session.playlist_container()
            self.debug('Populated playlists')
            self.login_dfr.callback(True)

    def logged_out(self, session):
        """
        Called on logout

        Makes sure we exit the main loop properly so the thread
        terminates.
        """
        self.debug('Logged out from spotify')
        self.finished = True
        self.awoken.set()

    def metadata_updated(self, sess):
        pass

    def connection_error(self, sess, error):
        pass

    def message_to_user(self, sess, message):
        pass

    def notify_main_thread(self, sess):
        self.awoken.set()

    def music_delivery(self, sess, frames, frame_size, num_frames, sample_type, sample_rate, channels):
        pass

    def play_token_lost(self, sess):
        pass

    def log_message(self, sess, data):
        pass

    def end_of_track(self, sess):
        pass



if __name__ == '__main__':
    import sys
    import optparse
   
    option_parser = optparse.OptionParser(version="%prog 0.1")
    option_parser.add_option("-u", "--username", help="spotify username")
    option_parser.add_option("-p", "--password", help="spotify password")
    options, args = option_parser.parse_args()

    if not options.username or not options.password:
        option_parser.print_help()
        sys.exit(1)
    
    client = SpotifyClient(options.username, options.password)
    client.start()

    time.sleep(5)
    for playlist in client.playlists:
        print playlist.name()
    client.disconnect()

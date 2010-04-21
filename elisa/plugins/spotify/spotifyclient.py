import sys
import os
import time
import pyspotify as spotify
import threading
from twisted.internet import reactor, defer, error
from elisa.core.log import Loggable
import gobject, sys
gobject.threads_init()
import pygst
#pygst.require('0.10')
import gst

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
        self.gst_push_data = threading.Event()

        self.playlists = []
        self.song_queue = []
        self.session = None

        self.connected = False
        self.login_failed = False
        self.playing = False

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
        """ 
        The main loop. This processes events and then either waits for an
        event. The event is either triggered by a timer expiring, or by a
        notification from within the spotify subsystem (it calls the wake
        method below). 
        """
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

    def load_track(self, uri):
        track = spotify.Link.from_string(uri).as_track()
        while not track.is_loaded():
            self.debug('Track is not loaded')
            time.sleep(0.5)
        self.debug("Track is loaded")
        self.session.load(track)
        

    # GST methods

    def gst_setup_source(self, player, sourceinfo):
        self.debug('Gst source creation callback')
        source = player.get_by_name(sourceinfo.name)
        caps = gst.caps_from_string(
            "audio/x-raw-int, "
            "endianness = (int) 1234, "
            "signed = (boolean) TRUE, "
            "width = (int) 16, "
            "depth = (int) 16, "
            "rate = (int) 44100, "
            "channels = (int) 2; "
        )
        source.set_property('caps', caps)
        source.set_property('max-bytes', 2000000)
        #source.set_property('stream-type', 1) # GST_APP_STREAM_TYPE_SEEKABLE

        source.connect('need-data', self.gst_need_data)
        source.connect('enough-data', self.gst_enough_data)
        source.connect('seek-data', self.gst_seek_data)
        self.gst_source = source

    def gst_enough_data(self, source):
        self.debug('Gst buffer saturated, pause pushing')
        self.gst_push_data.clear()

    def gst_need_data(self, source, size):
        self.debug('Gst buffer needs data, resume pushing')
        self.gst_push_data.set()

    def gst_seek_data(self, source, offset):
        self.debug('Gst buffer needs data, resume pushing')
        self.gst_push_data.set()

    def gst_state_changed(self, player, status):
        self.debug('Gst state change: %s' % status)
        if status in [player.PLAYING, player.BUFFERING, player.PREROLLING]:
            self.debug('Gst resuming play')            
            self.session.play(True)
        else:
            self.debug('Gst pause or stop')            
            self.session.play(False)
            self.gst_push_data.clear()
        return True

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
        self.debug('Spotify metadata updated')
        self.awoken.set()

    def connection_error(self, sess, error):
        self.debug('Spotify connection error: %s' % error)

    def message_to_user(self, sess, message):
        self.debug('Spotify message: %s' % message)

    def notify_main_thread(self, sess):
        self.awoken.set()

    def music_delivery(self, sess, frames, frame_size, num_frames, sample_type, sample_rate, channels):
        self.debug('Spotify music delivery')
        if not self.gst_push_data.is_set():
            self.debug('Asking spotify to retry later')
            return 0

        self.debug('Pushing frames to gst source')
        self.gst_source.emit('push-buffer', gst.Buffer(frames))
        return num_frames

    def play_token_lost(self, sess):
        self.debug('Spotify play token lost')


    def log_message(self, sess, data):
        self.debug('Spotify log message: %s' % data)


    def end_of_track(self, sess):
        self.debug('Spotify end of stream reached')
        self.gst_source.emit('end-of-stream')
        self.session.play(False)
        


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

    # Gst needs a main loop. No GUI so gobject loop is fine
    mainloop = gobject.MainLoop()

    uri = "spotify:track:5RrgzrzB9Mq1C095cIqgJc" # Good stuff
 
    # Create a playbin gst pipeline, give it the special appsource
    # uri, and make sure the client gets notified when gst has created
    # the source.
    player = gst.element_factory_make("playbin", "player")
    player.set_property('uri', 'appsrc://')
    player.connect('notify::source', client.gst_setup_source) 

    # Make gst ask for data
    player.set_state(gst.STATE_PLAYING)    

    # Make spotify produce data
    client.play_track(uri)

    try:
        print 'Entering mainloop'
        mainloop.run()
    except KeyboardInterrupt:
        print 'Exited mainloop'
    finally:
        print 'Cleaning up'
        client.session.play(False)
        player.set_state(gst.STATE_NULL)    
        client.disconnect()
        time.sleep(5)

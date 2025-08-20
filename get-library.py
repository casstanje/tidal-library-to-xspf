
import logging
from pathlib import Path
import csv
import time
import sys

import tidalapi

from tkinter import Tk
from tkinter.filedialog import askdirectory

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

oauth_file1 = Path("tidal-session.json")
oauth_file2 = Path("tidal-session-B.json")


class TidalSession:
    def __init__(self):
        self._active_session = tidalapi.Session()

    def get_uid(self):
        return self._active_session.user.id

    def get_session(self):
        return self._active_session


class TidalTransfer:
    def __init__(self):
        self.session_src = TidalSession()

    
    def export_xspf(self, my_playlists):
        logger.info("Exporting user library to xspf...")
        Tk().withdraw()
        folder = askdirectory()
        # save to csv file
        for playlist in my_playlists:
            tracks = playlist.tracks()
            filename = "".join(c for c in playlist.name.lower() if c.isalnum() or c in (' ', '.', '_')).rstrip().replace(" ", "-") + ".xspf"
            with open(folder + "/" + filename, "w") as f:
                print("")
                print("-----")
                print("Generating file for playlist: {title}...".format(title=playlist.name))
                f.writelines([
                    "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n",
                    "<playlist version=\"1\" xmlns=\"http://xspf.org/ns/0/\">\n",
                    "<title>{title}</title>\n".format(title=playlist.name.replace("&", "And").replace("<", "&lt;").replace(">", "&gt;")),
                    "   <trackList>\n"
                ])
                for track in tracks:
                    f.writelines([
                        "       <track>\n"
                        "           <title>{title}</title>\n".format(title=track.name).replace("&", "And"),
                        "           <location>tidal:{id}</location>\n".format(id=track.id),
                        "           <duration>{duration}</duration>\n".format(duration=(str(int(track.duration) * 1000))),
                        "           <album>{album}</album>\n".format(album=track.album.name).replace("&", "And"),
                        "           <creator>{artist}</creator>\n".format(artist=track.artist.name).replace("&", "And"),
                        "       </track>\n",
                    ])
                    print("Added track: {id}: {artist} - {album} - {title}...".format(id=track.id, artist=track.artist.name, album=track.album.name, title=track.name))
                f.writelines([
                    "   </trackList>\n",
                    "</playlist>\n",
                ])

    def do_transfer(self):
        # do login for src and dst Tidal account
        session_src = self.session_src.get_session()
        logger.info("Login to user (source)...")
        if not session_src.login_session_file(oauth_file1):
            logger.error("Login to Tidal user...FAILED!")
            exit(1)

        # get current user favourites (source)
        my_playlists = session_src.user.playlists()

        # export to xspf
        self.export_xspf(my_playlists)


if __name__ == "__main__":
    TidalTransfer().do_transfer()

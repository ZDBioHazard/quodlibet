# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation

from tests import TestCase
from .helper import visible

from gi.repository import Gtk

from quodlibet.qltk.songlistcolumns import create_songlist_column
from quodlibet.qltk.songmodel import PlaylistModel
from quodlibet.formats import AudioFile
import quodlibet.config


class TSongListColumns(TestCase):
    def setUp(self):
        quodlibet.config.init()

    def tearDown(self):
        quodlibet.config.quit()

    def _render_column(self, column, **kwargs):
        view = Gtk.TreeView()
        model = PlaylistModel()
        view.set_model(model)
        song = AudioFile({"~filename": "/dev/null", "~#rating": 0.6666,
                          "~#energy": 0.6666})
        song.update(kwargs)
        model.append(row=[song])
        view.append_column(column)
        if column.get_resizable():
            column.set_expand(True)

        with visible(view):
            view.columns_autosize()

        text = column.get_cells()[0].get_property("text")
        self.assertIsNot(text, None)
        return text

    def test_date(self):
        column = create_songlist_column("~#added")
        self._render_column(column)

        # column reuse triggers warning somwhow
        column = create_songlist_column("~#added")
        self._render_column(column, **{"~#added": 100})

    def test_length(self):
        column = create_songlist_column("~length")
        self._render_column(column)

    def test_filesize(self):
        column = create_songlist_column("~#filesize")
        self._render_column(column)

    def test_rating(self):
        column = create_songlist_column("~rating")
        text = self._render_column(column)
        self.assertNotEqual(text, "0.67")

        column = create_songlist_column("~#rating")
        text = self._render_column(column)
        self.assertEqual(text, "0.67")

    def test_energy(self):
        column = create_songlist_column("~energy")
        text = self._render_column(column)
        self.assertNotEqual(text, "0.67")

        column = create_songlist_column("~#energy")
        text = self._render_column(column)
        self.assertEqual(text, "0.67")

    def test_bitrate(self):
        column = create_songlist_column("~#bitrate")
        self._render_column(column)

    def test_basename(self):
        column = create_songlist_column("~basename")
        self._render_column(column)

    def test_pattern(self):
        column = create_songlist_column("<artist>-<album>")
        self._render_column(column)

    def test_artist(self):
        column = create_songlist_column("artist")
        self._render_column(column)

    def test_people(self):
        column = create_songlist_column("~people")
        self._render_column(column)

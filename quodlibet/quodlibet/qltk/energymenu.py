# -*- coding: utf-8 -*-
# Copyright 2011-2016 Nick Boultbee
#           2005 Joe Wreschnig
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from gi.repository import Gtk

from quodlibet import _
from quodlibet import util
from quodlibet import config
from quodlibet import qltk
from quodlibet.config import ENERGY
from quodlibet.qltk import Icons
from quodlibet.qltk import SeparatorMenuItem


class ConfirmEnergyMultipleDialog(qltk.Message):
    def __init__(self, parent, action_title, count, value):
        assert count > 1

        title = (_("Are you sure you want to change the "
                   "energy of all %d songs?") % count)
        desc = (_("The saved energy will be removed") if value is None
                else _("The energy of all selected songs will be changed to "
                       "'%s'") % util.format_energy(value))

        super(ConfirmEnergyMultipleDialog, self).__init__(
            Gtk.MessageType.WARNING, parent, title, desc, Gtk.ButtonsType.NONE)

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(action_title, Gtk.ResponseType.YES)


class EnergyMenuItem(Gtk.ImageMenuItem):

    def __init__(self, songs, library, label=_("_Energy")):
        super(EnergyMenuItem, self).__init__(label=label, use_underline=True)
        self._songs = songs
        image = Gtk.Image.new_from_icon_name(Icons.MEDIA_SEEK_FORWARD,
                                             Gtk.IconSize.MENU)
        image.show()
        self.set_image(image)

        submenu = Gtk.Menu()
        self.set_submenu(submenu)
        self._energy_menu_items = []
        for i in ENERGY.all:
            text = "%0.2f\t%s" % (i, util.format_energy(i))
            itm = Gtk.CheckMenuItem(label=text)
            itm.energy = i
            submenu.append(itm)
            handler = itm.connect(
                'toggled', self._on_energy_change, i, library)
            self._energy_menu_items.append((itm, handler))
        reset = Gtk.MenuItem(label=_("_Remove energy"), use_underline=True)
        reset.connect('activate', self._on_energy_remove, library)
        self._select_energy()

        submenu.append(SeparatorMenuItem())
        submenu.append(reset)
        submenu.show_all()

    def set_songs(self, songs):
        """Set a new set of songs affected by the energy menu"""
        self._songs = songs
        self._select_energy()

    def _select_energy(self):
        energy = [song("~#energy") for song in self._songs
                   if song and song.has_energy]
        song_count = len(self._songs)
        for (menu_item, handler) in self._energy_menu_items:
            energy_val = menu_item.energy
            energy_count = energy.count(energy_val)
            menu_item.handler_block(handler)
            if energy_count == 0:
                menu_item.set_active(False)
            elif energy_count == song_count:
                menu_item.set_active(True)
            else:
                menu_item.set_inconsistent(True)
            menu_item.handler_unblock(handler)

    def _on_energy_change(self, menuitem, value, library):
        self.set_energy(value, self._songs, library)

    def _on_energy_remove(self, menutitem, library):
        self.remove_energy(self._songs, library)

    def set_energy(self, value, songs, librarian):
        count = len(songs)
        if (count > 1 and
                config.getboolean("browsers", "energy_confirm_multiple")):
            parent = qltk.get_menu_item_top_parent(self)
            dialog = ConfirmEnergyMultipleDialog(
                parent, _("Change _Energy"), count, value)
            if dialog.run() != Gtk.ResponseType.YES:
                return
        for song in songs:
            song["~#energy"] = value
        librarian.changed(songs)

    def remove_energy(self, songs, librarian):
        count = len(songs)
        if (count > 1 and
                config.getboolean("browsers", "energy_confirm_multiple")):
            parent = qltk.get_menu_item_top_parent(self)
            dialog = ConfirmEnergyMultipleDialog(
                parent, _("_Remove Energy"), count, None)
            if dialog.run() != Gtk.ResponseType.YES:
                return
        reset = []
        for song in songs:
            if "~#energy" in song:
                del song["~#energy"]
                reset.append(song)
        librarian.changed(reset)

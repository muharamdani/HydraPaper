from gi.repository import Gtk


class HpSearchBar(Gtk.SearchBar):
    def __init__(self, toggle: Gtk.ToggleButton):
        self.toggle = toggle
        self.entry = Gtk.SearchEntry()
        super().__init__(hexpand=True, search_mode_enabled=False)
        self.set_child(self.entry)
        self.connect_entry(self.entry)
        self.toggle.connect('toggled', self.on_toggle_toggled)
        self.connect(
            'notify::search-mode-enabled', self.on_search_mode_toggled
        )

    def get_text(self) -> str:
        return self.entry.get_text()

    def on_toggle_toggled(self, *args):
        self.set_search_mode(self.toggle.get_active())

    def on_search_mode_toggled(self, *args):
        self.toggle.set_active(self.get_search_mode())

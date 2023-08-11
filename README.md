# <a href="https://hydrapaper.gabmus.org"><img height="32" src="data/icons/org.gabmus.hydrapaper.svg" /> HydraPaper</a>

Wallpaper manager with multimonitor support

![screenshot](https://gitlab.gnome.org/GabMus/HydraPaper/-/raw/website/website/screenshots/mainwindow.png)

## Installing

[![Packaging status](https://repology.org/badge/vertical-allrepos/hydrapaper.svg)](https://repology.org/project/hydrapaper/versions)

HydraPaper officially supports the following desktop environments:

- GNOME 3
- MATE
- Cinnamon
- Budgie

Experimental support for the sway window manager/Wayland compositor is also present.

### Flatpak universal package

[Install **Flatpak** by following the quick setup guide](https://flatpak.org/setup/).

Click the following button install HydraPaper from the Flathub store.

[![Get it on Flathub](https://raw.githubusercontent.com/flatpak-design-team/flathub-mockups/master/assets/download-button/download.svg?sanitize=true)](https://flathub.org/apps/details/org.gabmus.hydrapaper)

### Installing on Arch Linux and Arch based distros

You can find HydraPaper on AUR, as `hydrapaper-git` ([AUR page](https://aur.archlinux.org/packages/hydrapaper-git)).

### Installing on Fedora

[Fedora (official repo)](https://apps.fedoraproject.org/packages/hydrapaper): `sudo dnf install hydrapaper`

### Other distros

Your best bet is installing via Flatpak. [Check the instructions in the Flatpak section](#flatpak-universal-package).

Alternatively ou can either run HydraPaper without installing it (refer to the [Building for testing section](#building-for-testing)), or install it in your system (refer to the [Installing systemwide directly section](#build-and-install-systemwide-directly)).

## Dependencies

HydraPaper has these dependencies:

- python3
- python-pillow
- libadwaita
- gtk4
- pandoc (optional, needed to build the man page)

### Building and run from source

**Note**: If you're looking to install the app for regular use, [download it from Flathub](https://flathub.org/apps/details/org.gabmus.gfeeds) or from your distribution repositories. These instructions are only for developers and package maintainers.

```bash
git clone https://gitlab.gnome.org/GabMus/hydrapaper
cd hydrapaper
mkdir build
cd build
meson .. -Dprefix="$PWD/build/mprefix"
ninja install
ninja run
```

## Hacking

HydraPaper is developed and officially distributed using Flatpak. To hack on HydraPaper, it's highly recommended to use [GNOME Builder](https://www.gtk.org/docs/dev-tools/gnome-builder/). Open it up, clone this repo and run the app using the play button at the top of the window.

You might want to check your code with [flake8](https://github.com/pycqa/flake8) before opening a merge request.

```bash
flake8 hydrapaper
```

% HydraPaper(1) | General Commands Manual

NAME
====

HydraPaper - Wallpaper manager with multi monitor support

SYNOPSIS
========

`hydrapaper [-h] [-c WALLPAPER_PATH [WALLPAPER_PATH ...]] [-m WALLPAPER_MODES [WALLPAPER_MODES ...]] [-r] [-l]`

DESCRIPTION
===========

HydraPaper is a wallpaper manager, specifically designed to work around the lack of functionality of many desktop environments to set a different wallpaper for each monitor in a multi monitor setup. It accomplishes this by scaling and merging different wallpapers into a single one and setting it as spanned.

It currently supports various desktop environments, including GNOME, MATE, Cinnamon and Budgie. Experimental support is included for the sway window manager.

OPTIONS
=======

`-h, --help`

:   Show the help message and exit

`-c, --cli WALLPAPER_PATHS...`

:   Set wallpapers from the command line

`-m, --modes WALLPAPER_MODES...`

:   Specify the modes for the wallpapers (`zoom`, `center_black`, `center_blur`, `fit_black`, `fit_blur`)

`-r, --random`

:   Set wallpapers randomly

BUGS
====

Bugs can be reported and filed at https://gitlab.gnome.org/gabmus/hydrapaper/issues

If you are not using the flatpak version of HydraPaper, or if you are using an otherwise out of date or downstream version of it, please make sure that the bug you want to report hasn't been already fixed or otherwise caused by a downstream patch.

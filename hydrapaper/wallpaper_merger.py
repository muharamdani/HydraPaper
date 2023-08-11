from typing import Optional
from PIL import Image
from PIL.ImageOps import fit
from PIL.ImageFilter import GaussianBlur
from os import environ as Env
from subprocess import run
import re
from hydrapaper.confManager import ConfManager
from hydrapaper.get_gnome_dark_mode import get_gnome_dark_mode
from hydrapaper.is_flatpak import is_flatpak
# from .set_wallpaper_portal import set_wallpaper

SWAY_CONF_PATH = f'{Env.get("HOME")}/.config/sway/config'
SWAYLOCK_CONF_PATH = f'{Env.get("HOME")}/.swaylock/config'

confman = ConfManager()


def cut_image(image_path, resolution, save_path):
    with Image.open(image_path) as image:
        n_image = fit(
            image,
            resolution,
            method=Image.LANCZOS, centering=(0.5, 0.5)
        )
        n_image.save(save_path)


def get_combined_resolution(monitors):
    return (
        max([
            (m.offset_x + m.width) * m.scaling for m in monitors
        ]),
        max([
            (m.offset_y + m.height) * m.scaling for m in monitors
        ])
    )


def get_center_offset(img, bg):
    return (
        int((bg.width/2)-(img.width/2)),
        int((bg.height/2)-(img.height/2))
    )


def resize_letterbox(img, sw, sh):
    nw = 0
    nh = 0
    # old, weird and error prone
    # portrait = (
    #     img.width == img.height and sw > sh) or img.width < img.height
    # )
    portrait = img.width / img.height < sw / sh
    if portrait:
        nh = sh
        nw = int((sh * img.width) / img.height)
    else:
        nw = sw
        nh = int((img.height * sw) / img.width)
    return img.resize((nw, nh))


def blur_img(img, sw, sh):
    blur_filter = GaussianBlur(radius=20)
    bg = fit(img.copy(), (sw, sh))
    blur_bg = bg.filter(blur_filter)
    return blur_bg


def multi_setup_pillow(monitors, save_path, wp_setter_func=None):
    images = list()
    for monitor in monitors:
        n_img = Image.open(monitor.wallpaper)
        if 'fit' in monitor.mode or 'center' in monitor.mode:
            if 'black' in monitor.mode:
                bg = Image.new('RGB', (monitor.width, monitor.height))
            else:  # if 'blur' in monitor.mode:
                bg = blur_img(n_img, monitor.width, monitor.height)
            if 'fit' in monitor.mode or (
                n_img.height > monitor.height or
                n_img.width > monitor.width
            ):
                n_img = resize_letterbox(n_img, monitor.width, monitor.height)
            bg.paste(
                n_img,
                get_center_offset(n_img, bg)
            )
            n_img = bg
        images.append(n_img)
    resolutions = [
        (m.width * m.scaling, m.height * m.scaling) for m in monitors
    ]
    offsets = [
        (m.offset_x * m.scaling, m.offset_y * m.scaling) for m in monitors
    ]

    final_image_width, final_image_height = get_combined_resolution(monitors)

    n_images = [
        fit(i, r, method=Image.LANCZOS) for i, r in zip(images, resolutions)
    ]
    final_image = Image.new('RGB', (final_image_width, final_image_height))
    for i, o in zip(n_images, offsets):
        final_image.paste(i, o)
    final_image.save(save_path)
    for i in images:
        i.close()


def __set_wallpaper_gsettings(gsettings_path, wp_key, mode_key, path, wp_mode):
    # set_wallpaper(path)
    # return
    cmd = 'gsettings set'
    if is_flatpak():
        cmd = 'flatpak-spawn --host ' + cmd
    for t in [(wp_key, path), (mode_key, wp_mode)]:
        run(
            '{0} {1} {2} "{3}"'.format(
                cmd, gsettings_path, t[0], t[1]
            ),
            shell=True
        )
    # return
    # gsettings = Gio.Settings.new(gsettings_path)
    # gsettings.set_string(wp_key, path)
    # gsettings.set_string(mode_key, wp_mode)


def set_wallpaper_gnome(
        path, wp_mode='spanned', set_dark: Optional[bool] = None
):
    if set_dark is False:
        set_dark = get_gnome_dark_mode()
    print(set_dark)
    __set_wallpaper_gsettings(
        gsettings_path=(
            'org.gnome.desktop.background'
        ),
        wp_key='picture-uri-dark' if set_dark else 'picture-uri',
        mode_key='picture-options',
        path='file://{}'.format(path),
        wp_mode=wp_mode
    )


def set_wallpaper_cinnamon(path, wp_mode='spanned'):
    __set_wallpaper_gsettings(
        gsettings_path=(
            'org.cinnamon.desktop.background'
        ),
        wp_key='picture-uri',
        mode_key='picture-options',
        path='file://{}'.format(path),
        wp_mode=wp_mode
    )


def set_wallpaper_mate(path, wp_mode='spanned'):
    __set_wallpaper_gsettings(
        gsettings_path='org.mate.background',
        wp_key='picture-filename',
        mode_key='picture-options',
        path=path,
        wp_mode=wp_mode
    )


def set_wallpaper_sway(monitors):
    conf_path = SWAY_CONF_PATH
    with open(conf_path) as fd:
        conf = fd.read()
        fd.close()
    n_conf = re.sub(r'output .* bg .*', '', conf).strip()
    n_conf += '\n' + '\n'.join([
        f'output {m.name} bg {m.wallpaper} fill' for m in monitors
    ])
    with open(conf_path, 'w') as fd:
        fd.write(n_conf)
        fd.close()
    run('sway reload'.split(' '))

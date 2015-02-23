#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc, xbmcgui, xbmcaddon
import os
import sys
import shutil

__settings__ = xbmcaddon.Addon('plugin.video.chinachu')

__plugin__ = __settings__.getAddonInfo('name')
__author__ = __settings__.getAddonInfo('author')
__version__ = __settings__.getAddonInfo('version')

if __name__ == '__main__':
    print "'%s: ver %s' setting manager" % (__plugin__, __version__)

    if sys.argv[1] == 'clear_thumbnail_cache':
        print 'Deleting thumbnail cache...'
        xbmc.executebuiltin('XBMC.StopScript(plugin.video.chinachu)')
        thumbnail_cache_dir = os.path.join(xbmc.translatePath('special://masterprofile/'), 'addon_data', os.path.basename(__settings__.getAddonInfo('path')), 'thumbnail/')
        progress = xbmcgui.DialogProgress()
        progress.create(__plugin__, 'Deleting thumbnails...')
        progress.update(0)
        if os.path.exists(thumbnail_cache_dir):
            shutil.rmtree(thumbnail_cache_dir)
        progress.update(99)
        xbmc.sleep(1000)
        progress.update(100)
        print 'done.'
        sys.exit(0)

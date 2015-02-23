#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc, xbmcgui, xbmcaddon
import os
import sys
import shutil
import urllib2
from urlparse import urljoin

__settings__ = xbmcaddon.Addon('plugin.video.chinachu')

__plugin__ = __settings__.getAddonInfo('name')
__author__ = __settings__.getAddonInfo('author')
__version__ = __settings__.getAddonInfo('version')

if __name__ == '__main__' and len(sys.argv) >= 2:
    print "'%s: ver %s' utility" % (__plugin__, __version__)

    if sys.argv[1] == 'clear_thumbnail_cache':
        print 'Deleting thumbnail cache...'
        progress = xbmcgui.DialogProgress()
        progress.create(__plugin__, 'Deleting thumbnails...')
        progress.update(0)
        xbmc.executebuiltin('XBMC.StopScript(plugin.video.chinachu)')
        thumbnail_cache_dir = os.path.join(xbmc.translatePath('special://thumbnails/'), os.path.basename(__settings__.getAddonInfo('path')))
        if os.path.exists(thumbnail_cache_dir):
            shutil.rmtree(thumbnail_cache_dir)
        progress.update(99)
        xbmc.sleep(1000)
        progress.update(100)
        print 'done.'
        sys.exit(0)

    if sys.argv[1] == 'delete_recorded' and len(sys.argv) == 4:
        file_name = sys.argv[2]
        file_id = sys.argv[3]

        dialog = xbmcgui.Dialog()
        if dialog.yesno(xbmc.getLocalizedString(122).encode('utf_8'), xbmc.getLocalizedString(433).encode('utf_8') % file_name, yeslabel=xbmc.getLocalizedString(117)):
            server_address = __settings__.getSetting('server_address')
            api_endpoint = urljoin(server_address, '/api/')
            opener = urllib2.build_opener(urllib2.HTTPHandler)

            print 'Deleting recorded file...'
            progress = xbmcgui.DialogProgress()
            progress.create(__plugin__, 'Deleting recorded file...')
            progress.update(0)

            try:
                req = urllib2.Request(api_endpoint + 'recorded/' + file_id + '/file.m2ts')
                req.get_method = lambda: 'DELETE'
                url = opener.open(req)
            except:
                xbmc.log('Failed to delete recoded file: %s' % file_id, level=xbmc.LOGERROR)
                progress.close()
                xbmcgui.Dialog().ok(xbmc.getLocalizedString(16205), xbmc.getLocalizedString(16206))
                sys.exit(1)

            progress.update(80)
            xbmc.sleep(400)

            try:
                req = urllib2.Request(api_endpoint + 'recorded/' + file_id + '.json')
                req.get_method = lambda: 'DELETE'
                url = opener.open(req)
            except:
                xbmc.log('Failed to delete recoded information: %s' % file_id, level=xbmc.LOGERROR)
                progress.close()
                xbmcgui.Dialog().ok(xbmc.getLocalizedString(16205), xbmc.getLocalizedString(16206))
                sys.exit(1)

            progress.update(100)
            print 'done.'

        sys.exit(0)

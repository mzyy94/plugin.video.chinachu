#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import os
import sys
import shutil
import datetime
import time
import simplejson as json
import urllib2
from urlparse import urljoin
from threading import Thread

__settings__ = xbmcaddon.Addon('plugin.video.chinachu')

__plugin__ = __settings__.getAddonInfo('name')
__author__ = __settings__.getAddonInfo('author')
__version__ = __settings__.getAddonInfo('version')

if __name__ == '__main__':
    print sys.version
    print "'%s: ver %s' initialized" % (__plugin__, __version__)


    server_address = __settings__.getSetting('server_address')
    if not server_address:
        __settings__.openSettings()
        server_address = __settings__.getSetting('server_address')

    api_endpoint = urljoin(server_address, '/api/')

    thumbnail_cache_dir = os.path.join(xbmc.translatePath('special://thumbnails/'), os.path.basename(__settings__.getAddonInfo('path')), './')
    if not os.path.exists(thumbnail_cache_dir):
        os.makedirs(thumbnail_cache_dir)

    def getThumbnail(video_id, sec):
        thumbnail_path = thumbnail_cache_dir + video_id + '.jpg'
        with open(thumbnail_path, "wb") as thumbnail_file:
            try:
                thumbnail_data = urllib2.urlopen(api_endpoint + 'recorded/' + video_id + '/preview.jpg?pos=' + str(sec))
            except:
                xbmc.log('No thumbnail of %s' % video_id, level=xbmc.LOGWARNING)
            else:
                thumbnail_file.write(thumbnail_data.read())


    force_set_episode = __settings__.getSetting('force_set_episode') == 'true'
    channel_field = __settings__.getSetting('channel_field')

    if channel_field == xbmc.getLocalizedString(20339).encode('utf_8'):
        ch_field = 'director'
    elif channel_field == xbmc.getLocalizedString(20417).encode('utf_8'):
        ch_field = 'writer'
    #elif channel_field == xbmc.getLocalizedString(572).encode('utf_8'):
    else:
        ch_field = 'studio'


    watch_query = '?ext=m2ts'
    info = {}

    if __settings__.getSetting('video_encode') == 'false':
        watch_query += '&c:v=copy'
    else:
        video_codec = __settings__.getSetting('video_codec')
        video_size = __settings__.getSetting('video_size')
        video_bitrate = __settings__.getSetting('video_bitrate')
        if video_codec == 'H.264':
            watch_query += '&c:v=libx264'
        elif video_codec == 'MPEG-2':
            watch_query += '&c:v=mpeg2video'
        watch_query += '&b:v=' + video_bitrate + 'k'
        watch_query += '&s=' + video_size
        info['video'] = {
                'codec': video_codec.replace('-','').replace('.','').lower(),
                'width': video_size.split('x')[0],
                'height': video_size.split('x')[1],
                'aspect': round(16./9., 2)
                }


    if __settings__.getSetting('audio_encode') == 'false':
        watch_query += '&c:a=copy'
    else:
        audio_codec = __settings__.getSetting('audio_codec')
        if audio_codec == 'AAC':
            watch_query += '&c:a=libfdk_aac'
        elif audio_codec == 'Vorbis':
            watch_query += '&c:a=libvorbis'
        watch_query += '&b:a=' + __settings__.getSetting('audio_bitrate') + 'k'
        info['audio'] = {'codec': audio_codec.lower()}


    addon_handle = int(sys.argv[1])

    xbmcplugin.setPluginFanart(addon_handle, color1='0xFFEB6EA5', color2='0xFFEB6EA5', color3='0xFFEB6EA5')
    xbmcplugin.setContent(addon_handle, 'episodes')

    response = urllib2.urlopen(api_endpoint + 'recorded.json')
    strjson = response.read()
    data = json.loads(strjson)

    show_thumbnail = __settings__.getSetting('show_thumbnail') == 'true'
    get_thumb_queue = []

    for video in data:
        url = api_endpoint + 'recorded/' + video['id'] + '/watch.m2ts' + watch_query
        li = xbmcgui.ListItem(video['title'])

        startdate = datetime.datetime.fromtimestamp(video['start'] / 1000)
        duration = ((video['end'] - video['start']) / 1000)
        fulltitle = video['title'] if 'fullTitle' not in video else video['fullTitle']
        channel = video['channel']['name']

        if show_thumbnail:
            thumbnail_path = thumbnail_cache_dir + video['id'] + '.jpg'
            if not os.path.exists(thumbnail_path):
                get_thumb_queue.append(Thread(target=getThumbnail, args=(video['id'], duration / 10)))
            li.setIconImage(thumbnail_path)
            li.setThumbnailImage(thumbnail_path)
            li.setArt({'poster': thumbnail_path, 'fanart': thumbnail_path, 'landscape': thumbnail_path, 'thumb': thumbnail_path})

        li.setInfo('video', {
            'title': fulltitle,
            'originaltitle': fulltitle,
            'sorttitle': video['title'],
            'tvshowtitle' : video['title'],
            'album' : video['title'],
            'genre': video['category'],
            ch_field: channel,
            'plot': video['detail'],
            'year': startdate.strftime('%Y'),
            'duration': ('%d' % (duration / 60)),
            'date': startdate.strftime('%d.%m.%Y'),
            'aired': startdate.strftime('%Y-%m-%d'),
            'dateadded': startdate.strftime('%Y-%m-%d %H:%M:%S'),
            })
        if 'episode' in video and video['episode'] > 0:
            li.setInfo('video', {'episode': video['episode']})
        elif force_set_episode:
            li.setInfo('video', {'episode': 1})

        li.addStreamInfo('video', {'duration': duration})
        if 'video' in info:
            li.addStreamInfo('video', info['video'])
        if 'audio' in info:
            li.addStreamInfo('audio', info['audio'])

        li.addContextMenuItems([(xbmc.getLocalizedString(117), 'RunScript(%s/utility.py, delete_recorded, "%s", %s)' % (__settings__.getAddonInfo('path'), video['title'], video['id']))])

        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, totalItems=len(data))

    xbmcplugin.endOfDirectory(addon_handle)

    if show_thumbnail:
        queue_length = len(get_thumb_queue)
        __settings__.setSetting('thumbnail_downloding', str(queue_length))

        progress = xbmcgui.DialogProgressBG()
        progress.create(__plugin__, 'Downloading thumbnails...')
        progress.update(0)
        for i, q in enumerate(get_thumb_queue):
            q.start()
            progress.update(i * 100 / queue_length, message=('Downloading thumbnails... (%d/%d)' % (i + 1, queue_length)))
            q.join()
            xbmc.sleep(3000)
            thumbnail_downloding = int(__settings__.getSetting('thumbnail_downloding'))
            if thumbnail_downloding < queue_length:
                break
        progress.close()

    sys.modules.clear()

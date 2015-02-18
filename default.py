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

__settings__ = xbmcaddon.Addon('plugin.video.chinachu')

__plugin__ = __settings__.getAddonInfo('name')
__author__ = __settings__.getAddonInfo('author')
__version__ = __settings__.getAddonInfo('version')

print sys.version
print "'%s: ver %s' initialized" % (__plugin__, __version__)


server_address = __settings__.getSetting('server_address')
if not server_address:
    __settings__.openSettings()
    server_address = __settings__.getSetting('server_address')

api_endpoint = urljoin(server_address, '/api/')

video_codec = __settings__.getSetting('video_codec')
audio_codec = __settings__.getSetting('audio_codec')

watch_query = '?ext=m2ts'

if video_codec == '0':
    watch_query += '&c:v=copy'
else:
    if video_codec == '1':
        watch_query += '&c:v=libx264'
    elif video_codec == '2':
        watch_query += '&c:v=mpeg2video'
    watch_query += '&b:v=' + __settings__.getSetting('video_bitrate') + 'k'
    watch_query += '&s=' + __settings__.getSetting('video_size')

if audio_codec == '0':
    watch_query += '&c:a=copy'
else:
    if audio_codec == '1':
        watch_query += '&c:a=libfdk_aac'
    elif audio_codec == '2':
        watch_query += '&c:a=libvorbis'
    watch_query += '&b:a=' + __settings__.getSetting('audio_bitrate') + 'k'


addon_handle = int(sys.argv[1])

xbmcplugin.setContent(addon_handle, 'episodes')

response = urllib2.urlopen(api_endpoint + 'recorded.json')
strjson = response.read()
data = json.loads(strjson)

for video in data:
    url = api_endpoint + 'recorded/' + video['id'] + '/watch.m2ts' + watch_query
    li = xbmcgui.ListItem(video['title'])

    startdate = datetime.datetime.fromtimestamp(video['start'] / 1000)
    duration = ((video['end'] - video['start']) / 1000 / 60)
    fulltitle = video['title'] if 'fullTitle' not in video else video['fullTitle']
    channel = video['channel']['name']

    li.setInfo('video', {
        'title': fulltitle,
        'originaltitle': fulltitle,
        'sorttitle': video['title'],
        'tvshowtitle' : video['title'],
        'album' : video['title'],
        'genre': video['category'],
        'studio': channel,
        'director': channel,
        'plot': video['detail'],
        'year': startdate.strftime('%Y'),
        'duration': ('%d' % duration),
        'date': startdate.strftime('%d.%m.%Y'),
        'aired': startdate.strftime('%Y-%m-%d'),
        'dateadded': startdate.strftime('%Y-%m-%d %H:%M:%S'),
        })
    if 'episode' in video and video['episode'] > 0:
        li.setInfo('video', {'episode': video['episode']})

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)


xbmcplugin.endOfDirectory(addon_handle)
sys.modules.clear()

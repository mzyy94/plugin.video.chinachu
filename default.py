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

watch_query = '?ext=m2ts'
info = {}

if not __settings__.getSetting('video_encode'):
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


if not __settings__.getSetting('audio_encode'):
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

xbmcplugin.setContent(addon_handle, 'episodes')

response = urllib2.urlopen(api_endpoint + 'recorded.json')
strjson = response.read()
data = json.loads(strjson)

for video in data:
    url = api_endpoint + 'recorded/' + video['id'] + '/watch.m2ts' + watch_query
    li = xbmcgui.ListItem(video['title'])

    startdate = datetime.datetime.fromtimestamp(video['start'] / 1000)
    duration = ((video['end'] - video['start']) / 1000)
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
        'duration': ('%d' % (duration / 60)),
        'date': startdate.strftime('%d.%m.%Y'),
        'aired': startdate.strftime('%Y-%m-%d'),
        'dateadded': startdate.strftime('%Y-%m-%d %H:%M:%S'),
        })
    if 'episode' in video and video['episode'] > 0:
        li.setInfo('video', {'episode': video['episode']})

    li.addStreamInfo('video', {'duration': duration})
    if 'video' in info:
        li.addStreamInfo('video', info['video'])
    if 'audio' in info:
        li.addStreamInfo('audio', info['audio'])

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, totalItems=len(data))


xbmcplugin.endOfDirectory(addon_handle)
sys.modules.clear()

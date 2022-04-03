#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from urllib.request import urlopen
from urllib.parse import urlencode, unquote_plus
import simplejson as json

import xbmcgui
import xbmcplugin
import xbmcaddon

def getParameters(parameterString):
  commands = {}
  splitCommands = parameterString[parameterString.find('?') + 1:].split('&')
  for command in splitCommands:
    if (len(command) > 0):
      splitCommand = command.split('=')
      key = splitCommand[0]
      value = splitCommand[1]
      commands[key] = value
  return commands


def getLrtStreams():
  res = urlopen('https://www.lrt.lt/data-service/module/live/').read()
  data = json.loads(res)

  streams = {}
  for name, value in data['response']['data'].items():
    if value['type'] == 'video' and not name.startswith('LR'):
      streams[name] = {'title': value['title'], 'type': value['type'], 'url': value['content']}
  return streams

def getLnkStreams():
  res = urlopen('https://lnk.lt/api/main/content-page-by-program/tiesiogiai').read()
  live_config = json.loads(res)

  configs = []
  for component in live_config['components']:
    if component['type'] == 30:
      for channel in component['component']['channels']:
        configs.append(channel['episodeId'])

  streams = {}
  for config in configs:
    res = urlopen(f'https://lnk.lt/api/video/video-config/{config}').read()
    config = json.loads(res)
    name = config['videoInfo']['channel']
    title = config['videoInfo']['title']
    url = config['videoInfo']['videoFairplayUrl']
    streams[name] = {'title': title, 'type': 'video', 'url': url}

  return streams

def getMenuList():
  lrt_streams = getLrtStreams()
  lnk_streams = getLnkStreams()

  streams = lrt_streams.copy()
  streams.update(lnk_streams)

  for name, streamData in streams.items():
    listitem = xbmcgui.ListItem(name)
    listitem.setProperty('IsPlayable', 'true')

    info = { 'plot': streamData['title'] }
    streamType = 'audio' if streamData['type'] == 'radio' else 'video'
    listitem.setInfo(type = streamType, infoLabels = info )

    url = sys.argv[0] + '?' + urlencode({'mode': 1, 'url': streamData['url'], 'title': name})
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = url, listitem = listitem, isFolder = False, totalItems = 0)

  xbmcplugin.endOfDirectory(int(sys.argv[1]))


def playVideo(url, title):
  if not url:
    dialog = xbmcgui.Dialog()
    ok = dialog.ok( 'LRT Grotuvas' , 'Bloga vaizdo įrašo nuoroda "%s"!' % url )
    return

  listitem = xbmcgui.ListItem(label = title)
  listitem.setPath(url)
  xbmcplugin.setResolvedUrl(handle = int(sys.argv[1]), succeeded = True, listitem = listitem)


def main():
  params = getParameters(sys.argv[2])
  mode = None

  try:
    mode = int(params['mode'])
  except:
    pass

  if mode == None:
    getMenuList()
  elif mode == 1:
    url = unquote_plus(params['url'])
    title = unquote_plus(params['title'])
    playVideo(url, title)


main()
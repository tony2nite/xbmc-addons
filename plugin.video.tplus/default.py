'''
    t0mm0 test XBMC Addon
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import re
import string
import sys
import urlresolver
import urllib2
import xbmcplugin
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
from urlresolver import common


def get_movie_page(url, deep = False):
	success = False
	try:
		html = net.http_GET(url).content
		success = True
	except urllib2.HTTPError, e:
		 addon.log_debug('HTTP Error: %s' % e)
	
	if success:
		# get total pages
		p_r = '(\d+)</a></li><li title="Next Page".+?href="(.+?)(\d+)\/".+?<'
		pages_regex = re.finditer(p_r, html)
		total_pages = 1
		for s in pages_regex:
			total_pages, url, current_page = s.groups()
		#<div class="list_item.+?src="(.+?)".+?(frelease dvd|frelease) to get dvd symbol
		# scan items
		r = '<div class="list_item.+?src="(.+?)".+?(frelease dvd|frelease).+?<a class="plot".+?href="(.+?)".+?<b>(.+?)<\/b>(.+?)<.+?Rank: ([\d\.]+) Votes:(\d+).+?'
		regex = re.finditer(r, html, re.DOTALL)
		total_items = 0
		for s in regex:
			thumb, dvd, url, title, plot, rating, votes = s.groups()
			if dvd.find("dvd") != -1:
			    dvd = " (DVD)"
			else:
			    dvd = ""
			total_items += 1
			addon.add_directory({'mode': 'movie',
								 'url': base_url + url,
								 'imageurl': base_url + thumb},
								 {
								 'title': title + dvd,
								 'votes': int(votes),
								 'rating': float(rating),
								 'plotoutline': plot,
								 'secondlabel': dvd
								 },
								 img=base_url+thumb,
								 total_items=int(total_pages)*10)
		
		# get next page
		if deep == True:
			pages_regex = re.finditer(p_r, html)
			for s in pages_regex:
				total_pages, url, current_page = s.groups()
				print "%s page of %s" % (total_pages, current_page)
				get_movie_page(base_url + url + current_page + "/")

 
addon = Addon('plugin.video.tplus', sys.argv)
net = Net()


logo = os.path.join(addon.get_path(), 'art','logo.jpg')

base_url = 'http://tubeplus.me'

mode = addon.queries['mode']
play = addon.queries.get('play', None)
print "mode=" + mode
if play:
    url = addon.queries.get('url', '')
    host = addon.queries.get('host', '')
    media_id = addon.queries.get('media_id', '')
    #stream_url = urlresolver.resolve(play)
    stream_url = urlresolver.HostedMediaFile(url=url, host=host, media_id=media_id).resolve()
    addon.resolve_url(stream_url)

elif mode == 'resolver_settings':
    urlresolver.display_settings()


elif mode == 'tv':
    browse = addon.queries.get('browse', False)
    if browse == 'alpha':
        letter = addon.queries.get('letter', False)
        if letter:
            url = 'http://tubeplus.me/browse/tv-shows/All_Genres/%s/' % letter
            html = net.http_GET(url).content
            r = '<div class="list_item.+?src="(.+?)".+?<a class="plot".+?' + \
                'href="(.+?)".+?<b>(.+?)<\/b>.+?<\/b>(.+?)<'
            regex = re.finditer(r, html, re.DOTALL)
            for s in regex:
                thumb, url, title, plot = s.groups()
                addon.add_directory({'mode': 'series',
                                     'url': base_url + url},
                                     {'title': title},
                                     img=base_url+thumb)

        else:
            addon.add_directory({'mode': 'tv',
                                 'browse': 'alpha',
                                 'letter': '-'}, {'title': '#'})
            for l in string.uppercase:
                addon.add_directory({'mode': 'tv',
                                     'browse': 'alpha',
                                     'letter': l}, {'title': l})

    else:
        addon.add_directory({'mode': 'tv', 'browse': 'alpha'}, {'title': 'A-Z'})
        
elif mode == 'movies':
    
    xbmc.executebuiltin("Container.SetViewMode(%s)" % 'movies' )
    xbmcplugin.setContent( int( sys.argv[ 1 ] ), 'movies') 
    
    browse = addon.queries.get('browse', False)
    if browse == 'alpha':
        letter = addon.queries.get('letter', False)
        if letter:
            url = 'http://tubeplus.me/browse/movies/All_Genres/%s/' % letter
            url = addon.queries.get('next_url', url)
            get_movie_page(url, True)
        else:
            addon.add_directory({'mode': 'movies',
                                 'browse': 'alpha',
                                 'letter': '-'}, {'title': '#'})
            for l in string.uppercase:
                addon.add_directory({'mode': 'movies',
                                     'browse': 'alpha',
                                     'letter': l}, {'title': l})
    elif browse == 'latest':
        print 'latest'
        url = 'http://www.tubeplus.me/browse/movies/Last/ALL/'
        get_movie_page(url)
        
    elif browse == 'popular':
        print 'popular'
        categoryurl = addon.queries.get('categoryurl', False)
        if categoryurl:
            get_movie_page(categoryurl, False)
        else:
            url = 'http://www.tubeplus.me'
            html = net.http_GET(url).content
            
            r = '<div id="popular">.+?<ul>(.+?)<\/ul>'
            regex = re.findall(r, html, re.DOTALL)
            
            r = 'href="(.+)">(.+?)</a>'
            regex = re.finditer(r, regex[0])
            
            for s in regex:
                url, title = s.groups()
                addon.add_directory({'mode': 'movies',
                                     'browse': 'popular',
                                     'categoryurl': base_url + url}, {'title': title})
    else:
        addon.add_directory({'mode': 'movies', 'browse': 'alpha'}, {'title': 'A-Z'})
        
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_TITLE )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
        
elif mode == 'series':
    url = addon.queries['url']
    html = net.http_GET(url).content
    r = 'javascript:show_season\("(\d+?)","(.+?)"\)'
    regex = re.finditer(r, html, re.DOTALL)
    for s in regex:
        season, data = s.groups()
        episodes = data.split('||')
        for episode in episodes:
            params = episode.split('_')
            if len(params) == 5:
                ep_url = '%s/player/%s/' % (base_url, params[2])
                title = 'S%sE%s - %s (%s)' % (params[0], params[1],
                                              params[3], params[4])
                common.addon.log_debug('Episodes %s at %s' % (ep_url, title))
                addon.add_video_item({'url': ep_url}, {'title': title})
elif mode == 'movie':
    xbmc.executebuiltin("Container.SetViewMode(%s)" % 'movies' )
    
    url = addon.queries['url']
    html = net.http_GET(url).content
    
    r = "<h1>(.+?) \((\d+)\)</h1>.+<b>IMDB:</b>.+<span>tt(\d+)</span>"
    meta = re.findall(r, html, re.DOTALL)
    
    r = "<a.+?href=\"javascript:show\('(\w+?)','(.+?)', '(.+?)'.+?<b>(\d+)% said work.+?<\/b>"
    regex = re.finditer(r, html, re.DOTALL)
    for s in regex:
        id, title, host, quality = s.groups()
        addon.add_item({'host': host, 'media_id' : id},
                             {'title': u'%s (%s)' % (meta[0][0] , host),
                              'date': int(meta[0][1]),
                              'code': int(meta[0][2]),
                              'rating': float(quality),
                              'studio': host},
                              img=addon.queries['imageurl'],
                              is_folder=False,
                              item_type='video')
    xbmcplugin.setContent( int( sys.argv[ 1 ] ), 'movies') 
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_STUDIO )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )

elif mode == 'main':
#    addon.show_small_popup('t0mm0 test addon', 'Is now loaded enjoy', 6000, logo)
    addon.add_directory({'mode': 'tv'}, {'title': 'TUBE+ TV'})
    addon.add_directory({'mode': 'movies'}, {'title': 'TUBE+ Movies'})
    addon.add_directory({'mode': 'movies', 'browse': 'latest'}, {'title': 'TUBE+ Movies (Latest Releases)'})
    addon.add_directory({'mode': 'movies', 'browse': 'popular'}, {'title': 'TUBE+ Movies (Popular Categories)'})
    addon.add_directory({'mode': 'resolver_settings'}, {'title': 'Resolver Settings'}, is_folder=False)


if not play:
    addon.end_of_directory()


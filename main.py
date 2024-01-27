#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple website crawler to get URL list, Meta tags and <H1>
"""
__license__	= "MIT"
__author__	= "Sergey V Musenko"
__email__	= "sergey@musenko.com"
__copyright__= "© 2023, musenko.com"
__credits__	= ["Sergey Musenko"]
__date__	= "2024-01-23"
__version__	= "0.1"
__status__	= "prod"

import sys
import re
import requests
import time
import csv
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# settings
init_url  = "http://musenko.com"
save_file = 'crawl_{}.csv' # save results here
max_level = 10 # do not go deeper
use_pause = 0.3 # sleep before next reading

# to know where we start
init_url = init_url.rstrip('/')
initScheme = urlparse(init_url).scheme + '://'
initDomain = urlparse(init_url).netloc
slen = 0

# collect data here
results = {} # collect result here: { URL: { title, descr, keywords, h1, loadtime, link_count, level } }
headers = []
errors = []
mediafiles = []


def crawl_url( url, level = 0):
	global headers, results, slen, errors, mediafiles
	# get load time 1
	start_time = time.perf_counter()

	# tick next page load
	slen = max(slen, len(url))
	sys.stdout.write('  ' + str(len(results)) + '/' + str(level) + ' '+ url.ljust(slen) + "\r")

	# get page
	try:
		response = requests.get(url, allow_redirects=False) # with NO REDIRECTIONS !
		if response.status_code != 200:
			errors.append(url + f" (HTTP:{response.status_code})")
			return

		if 'text/html' not in response.headers['Content-Type'].lower():
			mediafiles.append(url)
			results[url] = {
				"title": 'mediafile',
				"description": response.headers['Content-Type'],
#				"keywords": '',
#				"h1": '',
			}
			return

	except BaseException as e:
		print(f'Error loading {url}', e)
		return

	# page loaded
	soup = BeautifulSoup(response.content, "html.parser")

	# get meta
	title = soup.find(re.compile("^title$", re.I))
	if bool(title): title = title.text.strip()

	descr = soup.find('meta', attrs = { 'name': re.compile("^description$", re.I) })
	if bool(descr): descr = descr.get('content').strip()

	keywd = soup.find('meta', attrs = { 'name': re.compile("^keywords$", re.I) })
	if bool(keywd): keywd = keywd.get('content').strip()

	h1 = soup.find(re.compile("^h1$", re.I))
	if bool(h1): h1 = h1.text.strip()

	# get links
	link_elements = soup.select("a[href]")
	link_count = len(link_elements)

	# get load time 2
	end_time = time.perf_counter()

	# store page attributes
	results[url] = {
		"title": title,
		"description": descr,
		"keywords": keywd,
		"h1": h1,
#		"loadtime": round(end_time - start_time, 3),
#		"linkcount": link_count,
#		"level": level
	}

	# prepare headers
	if not headers:
		headers = ['url'] + list(results[url].keys())

	# do not go deeper
	if level >= max_level:
		return

	# loop across extracted links
	for link in link_elements:
		next_url = link[ 'href' ].split("#")[0].split("?")[0].split("mailto:")[0].rstrip('/')

		domain = urlparse(next_url).netloc

		# is it containing a domain?
		if not domain:
			if next_url and next_url[0] != '/':
				# it is relative address with no leading '/'
				cut_url = url
				while next_url and next_url[0:3] == '../': # is uplevel
					next_url = next_url[3:]
					if len(cut_url.split('/')) > 3:
						cut_url = cut_url.replace('/' + cut_url.split('/')[-1], '')
				next_url = cut_url + '/' + next_url
			else: # it is empty or absolute 
				domain = initDomain
				next_url = initScheme + initDomain + next_url

		# is it foreign domain?
		elif domain != initDomain:
			continue

		# didn't we proceed it already?
		if not next_url in results:
			#print(next_url, '--', domain)
			# speed limit
			if use_pause:
				time.sleep(use_pause)
			# read next URL
			crawl_url(next_url, level + 1)
# def crawl_url -- end


def save_results():
	if not results:
		return

	# write file or print on screen?
	if save_file:
		to_file = save_file.format(urlparse(init_url).netloc)
		with open(to_file, 'w', newline='') as f:
			w = csv.writer(f)
			w.writerow(headers)
			for url, res in sorted(results.items()):
				w.writerow([url] + list(res.values()))
		print(f'Saved to "{to_file}"')

	else:
		print(headers)
		for url, res in sorted(results.items()):
			print([url] + list(res.values()))
# def save_results -- end


# start crawler
if __name__ == '__main__':
	print(f'Crawler start with "{init_url}"')
	crawl_url(init_url)

	print('Total:', len(results), 'pages'.ljust(slen))

	if len(mediafiles):
		print(len(mediafiles), 'media files')

	if len(errors):
		print(len(errors), 'errors:')
		for er in errors:
			print(f"\t{er}")

	save_results()

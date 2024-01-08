#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple website crawler to get Meta tags and <H1>

To Do:
- скрипт циклится в глубину!
- добавить вывод ошибок 404 not found
"""
__license__	= "GPL"
__author__	= "Sergey V Musenko"
__email__	= "sergey@musenko.com"
__copyright__= "© 2023, musenko.com"
__credits__	= ["Sergey Musenko"]
__date__	= "2023-10-17"
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
# init_url  = "https://www.24lottos.com" # initial URL, must be with domain
#init_url  = "http://24lottos.home"
init_url  = "http://musenko.com"
save_file = 'crawler_{}.csv' # save results here
max_level = 2 # do not go deeper
use_pause = 0.1 # sleep before next reading

# collect data here
results = {} # collect result here: { URL: { title, descr, keywords, h1, loadtime, link_count, level } }
headers = []

# to know where we start
init_url = init_url.rstrip( '/')
initScheme = urlparse( init_url).scheme + '://'
initDomain = urlparse( init_url).netloc
slen = 0


def crawl_url( url, level = 0):
	global headers, results, slen
	# get load time 1
	start_time = time.perf_counter()

	# tick next page load
	slen = max(slen, len(url))
	sys.stdout.write('  ' + str(len(results)) + ' ' + url.ljust(slen) + "\r")

	# get page
	try:
		response = requests.get(url, allow_redirects=False) # with NO REDIRECTIONS !

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
		next_url = link[ 'href' ].rstrip('/').split("#")[0].split("?")[0].split("mailto:")[0]

		domain = urlparse(next_url).netloc

		# is it containing a domain?
		if not domain:

			if bool(next_url) and next_url[0] != '/':
				# it is relative address with no leading '/'
				next_url = url + '/' + next_url
			else:
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
	save_results()

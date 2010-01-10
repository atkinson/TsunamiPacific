#
# 
#
#
#
# Based on: http://www.halotis.com/2009/07/01/rss-twitter-bot-in-python/

from time import strftime
import sqlite3
 
import twitter     #http://code.google.com/p/python-twitter/
import bitly       #http://code.google.com/p/python-bitly/
import feedparser  #available at feedparser.org
 
 
DATABASE = "pacificTsunami.sqlite"
 
BITLY_LOGIN = "bitlyUsername"
BITLY_API_KEY = "api key"
 
TWITTER_USER = "username"
TWITTER_PASSWORD = "password"
 
def print_stats():
	conn = sqlite3.connect(DATABASE)
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
 
	b = bitly.Api(login=BITLY_LOGIN,apikey=BITLY_API_KEY)
 
	c.execute('SELECT title, url, short_url from RSSContent')
	all_links = c.fetchall()
 
	for row in all_links:
 
		short_url = row['short_url']
 
		if short_url is None:
			short_url = b.shorten(row['url'])
			c.execute('UPDATE RSSContent SET `short_url`=? WHERE `url`=?',(short_url,row['url']))
 
 
		stats = b.stats(short_url)
		print "%s - User clicks %s, total clicks: %s" % (row['title'], stats.user_clicks,stats.total_clicks)
 
	conn.commit()
 
def tweet_rss(url):
 
	conn = sqlite3.connect(DATABASE)
	conn.row_factory = sqlite3.Row
	c = conn.cursor()
 
	#create the table if it doesn't exist
	c.execute('CREATE TABLE IF NOT EXISTS RSSContent (`url`, `title`, `dateAdded`, `content`, `short_url`)')
 
	api = twitter.Api(username=TWITTER_USER, password=TWITTER_PASSWORD)
	b = bitly.Api(login=BITLY_LOGIN,apikey=BITLY_API_KEY)
 
	d = feedparser.parse(url)
 
	for entry in d.entries:
 
		#check for duplicates
		c.execute('select * from RSSContent where url=?', (entry.link,))
		if not c.fetchall():
 
			tweet_text = "%s - %s" % (entry.title, entry.summary)
 
			shortened_link = b.shorten(entry.link)
 
			t = (entry.link, entry.title, strftime("%Y-%m-%d %H:%M:%S", entry.updated_parsed), entry.summary, shortened_link)
			c.execute('insert into RSSContent (`url`, `title`,`dateAdded`, `content`, `short_url`) values (?,?,?,?,?)', t)
			print "%s.. %s" % (tweet_text[:115], shortened_link)
 
			api.PostUpdate("%s.. %s" % (tweet_text[:115], shortened_link))
 
	conn.commit()
 
if __name__ == '__main__':
  tweet_rss('http://www.halotis.com/feed/')
  print_stats()
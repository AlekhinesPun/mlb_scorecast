from datetime import datetime
import urllib2
import xml.etree.ElementTree as et
import numpy as np

class gameScraper(object):
	def __init__(self,custom_date=False,fetch=True,save=False,mode='pbp'):
		self.mode = mode
		## To lookup a historical date, use custom date = (YYYY,MM,DD)
		## If to save time you want to manually lookup individual games, use fetch=False
		if custom_date:
			self.year,self.month,self.day = custom_date
		else:
			dt_temp = datetime.now()
			self.year,self.month,self.day = dt_temp.strftime('%Y'),dt_temp.strftime('%m'),dt_temp.strftime('%d')
		self.schedule = self._getSchedule()
		self.game_datas = {}
		if fetch:
			for game_id in self.schedule:
				self.game_datas[game_id] = self._getXML(game_id)
		elif save:
			for game_id in self.schedule:
				self._saveXML(game_id)

	def _getSchedule(self):
		## Semi-private method to lookup games on a particular day
		self.path = 'http://gd2.mlb.com/components/game/mlb/year_' + self.year + '/month_' + self.month + '/day_' + self.day + '/'
		req = urllib2.Request(self.path)
		schedule_page = urllib2.urlopen(req).read()
		game_ids = []
		for item in schedule_page.split('href="gid_')[1:]:
			game_ids.append(item.split('/">')[0])
		return game_ids

	def _getXML(self,game_id):
		## Semi-private method to lookup a game's xml and convert it into a list/dictionary structure that is default to ElementTree
		if self.mode == 'lin':
			game_path = self.path + 'gid_' + game_id + '/linescore.xml'
		elif self.mode == 'pbp':
			game_path = self.path + 'gid_' + game_id + '/inning/inning_all.xml'
		print game_path
		try:
			req = urllib2.Request(game_path)
			pbp_xml = urllib2.urlopen(req).read().split('-->')[1]
			game_data = et.fromstring(pbp_xml)
			return game_data
		except:
			return None

	def _saveXML(self,game_id,path='data/'):
		if self.mode == 'lin':
			game_path = self.path + 'gid_' + game_id + '/linescore.xml'
			path += 'linescores/'
		elif self.mode == 'pbp':
			game_path = self.path + 'gid_' + game_id + '/inning/inning_all.xml'
			path += 'playbyplays/'
		print game_path
		try:
			req = urllib2.Request(game_path)
			pbp_xml = urllib2.urlopen(req).read().split('-->')[1]
			f = open(path+game_id+'.xml','wb')
			f.write(pbp_xml)
			f.close()
			return
		except:
			return

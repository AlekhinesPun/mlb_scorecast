import pandas as pd
import xml.etree.ElementTree as ET
import os

def getPitches():
	# pid='572821'
	batter_dict = {}
	files = os.listdir('data/playbyplays/')
	pitches = []
	for fn in sorted(files):
		tree = ET.parse('data/playbyplays/'+fn)
		root = tree.getroot()
		for inning in root:
			for topbot in inning:
				for event in topbot:
					if event.tag == 'atbat':
						balls = 0
						strikes = 0
						if not event.attrib['batter'] in batter_dict:
							batter_dict[event.attrib['batter']] = []
						for it in event:
							if it.tag == 'pitch':
								out = it.attrib
								out['balls'] = balls
								out['strikes'] = strikes
								batter_dict[event.attrib['batter']].append(out)
								pitches.append(out)
								if out['type'] == 'B':
									balls += 1
								elif out['type'] == 'S':
									strikes += 1
		print fn
	return pitches,batter_dict

def getBaseStates():
	files = os.listdir('data/playbyplays/')
	states = {}
	for fn in sorted(files)[100:]:
		away_score,home_score = getScores(fn)
		if away_score==home_score:
			continue
		tree = ET.parse('data/playbyplays/'+fn)
		root = tree.getroot()
		bs = baseStates()
		for m,inning in enumerate(root):
			bs.top = True
			bs.inning = int(inning.attrib['num'])
			for topbot in inning:
				bs.outs = 0
				bs.state = 0
				compressed_state = bs.compressed_state()
				if not compressed_state in states:
					states[compressed_state] = []
				if bs.top ^ (home_score > away_score):
					states[compressed_state].append(1)
				else:
					states[compressed_state].append(0)
				for n,atbat in enumerate(topbot):
					if atbat.tag == 'atbat':
						bs.update_ab(atbat)
					elif atbat.tag == 'action' and n+1 == len(topbot) and m+1 == len(root):
						bs.update_ac(atbat)
					compressed_state = bs.compressed_state()
					if not compressed_state in states:
						states[compressed_state] = []
					if bs.top ^ (home_score > away_score):
						states[compressed_state].append(1)
					else:
						states[compressed_state].append(0)
				bs.top = False
		if (bs.away_score,bs.home_score)!=(away_score,home_score):
			print fn
			print (bs.away_score,bs.home_score),(away_score,home_score)
			return
	return states

class baseStates():
	def __init__(self):
		self.away_score,self.home_score = 0,0
		self.state = 0
		self.top = True
		self.inning = 1
		self.outs = 0
		self.base_dict = {'':0,'1B':1,'2B':2,'3B':4}

	def update_ab(self,atbat):
		self.outs = int(atbat.attrib['o'] or 0)
		self.state = 0
		for pitch in atbat:
			if pitch.tag == 'runner':
				# self.state -= self.base_dict[pitch.attrib['start']]
				self.state += self.base_dict[pitch.attrib['end']]
				if 'score' in pitch.attrib and pitch.attrib['score'] == 'T':
					if self.top:
						self.away_score += 1
					else:
						self.home_score += 1

	def update_ac(self,action):
		self.outs = int(action.attrib['o'] or 0)
		if 'score' in action.attrib and action.attrib['score'] == 'T':
			if self.top:
				self.away_score += 1
			else:
				self.home_score += 1

	def compressed_state(self,score_cutoff=4):
		if self.top:
			score_diff = self.away_score - self.home_score
		else:
			score_diff = self.home_score - self.away_score
		return min(score_cutoff,max(-score_cutoff,score_diff)) * 1000 + self.state * 100 + self.outs * 10 + min(self.inning,9)

def getScores(fn,path='data/linescores/'):
	tree = ET.parse(path+fn)
	root = tree.getroot()
	innings = []
	for i in root:
		if i.tag == 'linescore':
			innings.append(i)
	away_score = sum(int(i.attrib['away_inning_runs'] or 0) for i in innings)
	home_score = sum(int(i.attrib['home_inning_runs'] or 0) for i in innings)
	return away_score,home_score

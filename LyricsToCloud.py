import pandas as pd
import numpy as np
import urllib2
from bs4 import BeautifulSoup
from unidecode import unidecode
from tqdm import trange
import string
from collections import Counter
from wordcloud import WordCloud, STOPWORDS
import sys
import os
import configparser



SITE_BB = 'https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_'
SITE_LY = "http://lyrics.wikia.com/wiki/"
REQ_HDR = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
			   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
			  }



class LyricCloud(object):
	def __init__(self,start_year,end_year):
		self.start_year = int(start_year)
		self.end_year = int(end_year)
		self.load_configurations()
		if self.start_year < self._MIN_YR or self.end_year > self._MAX_YR:
			raise ValueError("\nYear must be greater or equal to 1960 and lower or equal to 2017.\nYour input :{}-{} \n" .format(self.start_year,self.end_year))
		if self.start_year > self.end_year:
			temp=self.start_year
			self.start_year = self.end_year
			self.end_year = temp


	def get_song_data(self):

		billboard_data=[]
		for year in trange(self.start_year, self.end_year+1,desc='Getting songs...'):
			response = urllib2.urlopen(SITE_BB + str(year))
			html = response.read()
			soup = BeautifulSoup(html, 'html.parser')

			#Find the correct table using class method
			table = soup.find('table', attrs={'class':'wikitable sortable'})
			rows = table.findChildren(['tr'])
			#Iteratore over all rows of the table
			for row in rows:
				curr_row = []
				#Song position and song year
				song_pos = ((len(billboard_data))%100)+1
				curr_row.extend([song_pos,year])
				cells = row.findChildren('td')
		
				for cell in cells:
					text = unidecode(cell.text).replace("\n","").replace("\"","")
					curr_row.append(text)							
					if len(curr_row)==4 and year >=1982:
						#Create Main_Artist feature
						curr_row.append(text.split("featuring", 1)[0].rstrip())
						#Add new row to data
						billboard_data.append(curr_row)

					#Ugly hack to make tables <1982 work properly
					elif len(curr_row)==5 and year <1982:
						del curr_row[2]
						#Create Main_Artist feature
						curr_row.append(text.split("featuring", 1)[0].rstrip())
						#Add new row to data
						billboard_data.append(curr_row)

		self.dataframe= pd.DataFrame(billboard_data,columns=['Position','Year','Title','Artist','Main Artist'])

	def get_song_lyrics(self):
		lyric_data=[]
		not_found=0
		for i in trange(0,self.dataframe.shape[0],desc='Getting lyrics..'):
			#Forming correct query Arist:Title , 'and' is parsed as '%26' on the site
			clean_artist =self.dataframe.loc[i]['Main Artist'].replace(" and "," %26 ")
			clean_title = self.dataframe.loc[i]['Title']
			query = (SITE_LY
					 +clean_artist
					 +":"
					 +clean_title).replace(" ","_")
			try:
					response = urllib2.Request(query,headers=REQ_HDR)
					page = urllib2.urlopen(response)
					html = page.read()
					soup = BeautifulSoup(html, 'html.parser')
					lyrics_box= soup.find('div',class_="lyricbox")
					#Replace <br> tags with white space
					for br in lyrics_box.find_all("br"):
						br.replace_with(" ")
					#using lower cases for uniformity
					lyric_data.append(lyrics_box.get_text().lower())
				
			except:
					#if site not found or other error : empty lryics
					lyric_data.append(" ")
					not_found+=1


		print("Lyrics not found:{}\nLyrics found:{}".format(not_found,len(lyric_data)-not_found))
		self.dataframe['Lyrics']=lyric_data


	def generate_world_cloud(self):


		#Join all lyrics into single string
		all_lyrics =""
		for i in trange(0,self.dataframe.shape[0],desc="Generating image.."):
			#Replace new space and eliminate punctuation
			all_lyrics=all_lyrics+" "+(self.dataframe.loc[i,'Lyrics'].replace("\n",""))
			for p in string.punctuation:
				all_lyrics = all_lyrics.replace(p,'')

			
		# #Filter stopwords from lyrics
		sw = set(STOPWORDS)

		
		# Generate world cloud
		wordcloud = WordCloud(font_path = self._FONT_PATH,
							  height=self._HEIGHT,
							  width=self._WIDTH,
							  background_color=self._BGC,
							  colormap =self._FONT_COLOR,
							  stopwords = sw,
							  relative_scaling=self._RELATIVE_SCALING,
							).generate(all_lyrics)


		if self.start_year == self.end_year:
			wordcloud.to_file('LyricCloud'+'_'+str(self.start_year)+'.png')
		else:
			wordcloud.to_file('LyricCloud'+'_'+str(self.start_year)+'_'+str(self.end_year)+'.png')


	def load_configurations(self):
		#Get file configurations
		config = configparser.ConfigParser()
		config.read('Config.ini')
		self._FONT_PATH =  config['IMAGE']['Font_path']
		if not os.path.exists(self._FONT_PATH):
			print("Impossible loading your font. Set to default.")
			self._FONT_PATH = None;
		self._RELATIVE_SCALING = float(config['IMAGE']['Relative_scaling'])
		self._FONT_COLOR = config['IMAGE']['Font_color']
		self._HEIGHT = int(config['IMAGE']['Height'])
		self._WIDTH = int(config['IMAGE']['Width'])
		self._BGC = config['IMAGE']['Background']
		self._MIN_YR =int(config['YEAR']['Min_year'])
		self._MAX_YR =int(config['YEAR']['Max_year'])





if __name__ == '__main__':

	if len(sys.argv) ==5:
		bb_mode = sys.argv[4]
	else :
		bb_mode = 'timespan'

	if sys.argv[1] == 'bb':
		if bb_mode == 'yearly':
			for i in range(int(sys.argv[2]),int(sys.argv[3])+1):
				lc = LyricCloud(i,i)
				lc.get_song_data()
				lc.get_song_lyrics()
				lc.generate_world_cloud()
		else :
			lc = LyricCloud(sys.argv[2],sys.argv[3])
			lc.get_song_data()
			lc.get_song_lyrics()
			lc.generate_world_cloud()

	elif sys.argv[1] == 'band':
		print("Not implemented yet")

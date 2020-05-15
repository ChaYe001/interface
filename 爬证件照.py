# !/usr/bin/env python
#coding=utf-8
import requests
import os
import re
from bs4 import BeautifulSoup

import argparse
import hashlib
import base64
import gzip
import time
import io
class YirenSpider(object):
	headers = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"}
	yiren_str = 'http://www.zybus.com/yirentuku'
	name_str = 'http://img.zybus.com/'
	html_suffix = '.html'
	def get_html_data(self,url):
		# print(url)
		text = requests.get(url,headers = self.headers)
		return text.content
	def get_soup(self,text):
		soup = BeautifulSoup(text, 'lxml')
		return soup
	def get_name_htmls(self,url):
		text = self.get_html_data(url)
		soup = self.get_soup(text)
		totals = soup.find_all('img')

		# print(totals)
		# img_url_list = []
		for link in totals:
			# a_link = link.get('href')
			a_name = link.get('alt')
			if a_name != 'None':
				return a_name
			else:
				return
			# print(a_name)
	def get_yiren_htmls(self,url):
		text = self.get_html_data(url)
		soup = self.get_soup(text)
		totals = soup.find_all('script')
		linklen = 0
		img_url_list=[]
		for link in totals:
			link = str(link)
			for linklen in range(len(link)) :

				# linklen = len(link)
				# print(link)
				a_link = link.find('hoverURL')
				# print(a_link)
				b_link = link[a_link:a_link+200].find('.jpg')
				# print(b_link)
				img_url_list.append(link[a_link + 11:a_link + b_link + 4])
				linklen = a_link + b_link + 4
				# link = link[a_link+b_link+4:linklen]
				# if a_link+b_link+4 >= linklen:
				# 	break
			# print(img_url_list)

		return img_url_list
	def get_timestr(self):
		time_now = int(time.time())
		time_local = time.localtime(time_now)
		dt = time.strftime("%Y-%m-%d_%H:%M:%S",time_local)
		return dt
	# def get_img_url(self,url):#得到 图片的 html 地址
	# 	# img_prefix = 'src'
	# 	# img_suffix ='.jpg'
	#
	# 	text = self.get_html_data(url)
	# 	soup = self.get_soup(text)
	# 	totals = soup.find_all('img')
	# 	img_urls = []
	# 	for link in totals:
	# 					img_url = link.get('src')
	# 		if img_url is not None:
	# 			img_urls.append(img_url)
	# 		#print(img_src[index+5:index_r+4])
	# 	# print(img_urls)
	# 	return img_urls

	def download_images(self,urls,dirpath):#保存到指定的 文件夹
		if not os.path.exists(dirpath):
			os.makedirs(dirpath)
		global i
		print('t: ',urls)
		u_img_data = self.get_html_data(urls)
			# print(u_img_data)
		suffix = 'jpg'

		with open(dirpath + '\\' + str(i) + '.' + suffix, 'wb') as f:
			f.write(u_img_data)
			print(i)
			i+=1
		# return

	def spider(self,url,dirpath):
		htmllist = self.get_yiren_htmls(url)#得到主页 艺人的html 地址
		print('123: ', htmllist)
		# htmllist = ['http://www.zybus.com/yirentuku/114501.html', 'http://www.zybus.com/yirentuku/114502.html', 'http://www.zybus.com/yirentuku/114503.html', 'http://www.zybus.com/yirentuku/114504.html', 'http://www.zybus.com/yirentuku/114505.html', 'http://www.zybus.com/yirentuku/114499.html', 'http://www.zybus.com/yirentuku/114497.html', 'http://www.zybus.com/yirentuku/114498.html', 'http://www.zybus.com/yirentuku/114495.html', 'http://www.zybus.com/yirentuku/114493.html', 'http://www.zybus.com/yirentuku/114492.html', 'http://www.zybus.com/yirentuku/114491.html', 'http://www.zybus.com/yirentuku/114490.html']
		global i
		i = 0
		for html in htmllist:
			if html != '':
				print(html)
				self.download_images(html,dirpath) #保存下来
				# pass


if __name__ == '__main__':
	url ='https://image.baidu.com/search/index?ct=201326592&cl=2&st=-1&lm=-1&nc=1&ie=utf-8&tn=baiduimage&ipn=r&rps=1&pv=&fm=rs1&word=%E8%93%9D%E5%BA%95%E8%AF%81%E4%BB%B6%E7%85%A7&oriquery=%E8%93%9D%E5%BA%95%E5%9B%BE%E7%89%87%E8%AF%81%E4%BB%B6%E7%BA%AF%E8%89%B2&ofr=%E8%93%9D%E5%BA%95%E5%9B%BE%E7%89%87%E8%AF%81%E4%BB%B6%E7%BA%AF%E8%89%B2&hs=2&sensitive=0'

	dir ='D:\\工作内容\\测试记录\\样本\\证件照1\\'
	# for url in urls:
	# print(url)
	Yiren = YirenSpider()
	# i = 0
	Yiren.spider(url,dir)
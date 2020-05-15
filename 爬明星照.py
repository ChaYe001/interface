# !/usr/bin/env python
# coding=utf-8
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
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"}
    yiren_str = 'http://www.zybus.com/yirentuku'
    name_str = 'http://img.zybus.com/'
    html_suffix = '.html'

    def get_html_data(self, url):
        # print(url)
        text = requests.get(url, headers=self.headers)
        return text.content

    def get_soup(self, text):
        soup = BeautifulSoup(text, 'lxml')
        return soup

    def get_name_htmls(self, url):
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

    def get_yiren_htmls(self, url):
        text = self.get_html_data(url)
        soup = self.get_soup(text)
        totals = soup.find_all('a')
        # print(totals)
        img_url_list = []
        for link in totals:
            a_link = link.get('href')
            print(a_link)
            # a_name = link.get('alt')
            # print(a_name)
            if a_link is not None:
                if len(a_link) >= (len(self.yiren_str) + len(self.html_suffix)) and a_link.startswith(self.yiren_str):
                    if len(img_url_list) == 0:
                        img_url_list.append(a_link)
                    # print(a_link)
                    else:
                        if img_url_list.count(a_link) > 0:
                            # print(a_link)
                            pass
                        else:
                            img_url_list.append(a_link)
        return img_url_list

    def get_timestr(self):
        time_now = int(time.time())
        time_local = time.localtime(time_now)
        dt = time.strftime("%Y-%m-%d_%H:%M:%S", time_local)
        return dt

    def get_img_url(self, url):  # 得到 图片的 html 地址
        # img_prefix = 'src'
        # img_suffix ='.jpg'

        text = self.get_html_data(url)
        soup = self.get_soup(text)
        totals = soup.find_all('img')
        img_urls = []
        for link in totals:
            # img_src = str(link)
            # print(totals)
            # img_src_len = len(img_src)
            # index = img_src.find(img_prefix)
            # print(index)
            # index_r = img_src.find(img_suffix)
            # print(index_r)
            # img_urls.append(img_src[index+5:index_r+4])
            img_url = link.get('src')
            if img_url is not None:
                img_urls.append(img_url)
            else:
                return
        # print(img_src[index+5:index_r+4])
        print(img_urls)
        return img_urls

    def download_images(self, urls, name, dirpath):  # 保存到指定的 文件夹
        if not os.path.exists(dirpath + name):
            os.makedirs(dirpath + name)
        i = 0
        for u in urls:
            # print('t: ',u)
            if len(u) >= len(self.name_str) and u.startswith(self.name_str):
                print('t: ', u)
                u_img_data = self.get_html_data(u)
                # print(u_img_data)
                suffix = 'jpg'
                # #suffix = suffix[len(suffix) - 1]
                # time.sleep(1)
                # filename = str(self.get_timestr())
                #
                # if os.path.exists(dirpath + name) is False:
                # 	os.mkdir(dirpath + name)
                with open(dirpath + name + '\\' + str(i) + '.' + suffix, 'wb') as f:
                    f.write(u_img_data)
                    print(i)
                    i += 1
            else:
                return

    # return

    def spider(self, url, dirpath):
        htmllist = self.get_yiren_htmls(url)  # 得到主页 艺人的html 地址
        print('123: ', htmllist)
        # htmllist = ['http://www.zybus.com/yirentuku/114501.html', 'http://www.zybus.com/yirentuku/114502.html', 'http://www.zybus.com/yirentuku/114503.html', 'http://www.zybus.com/yirentuku/114504.html', 'http://www.zybus.com/yirentuku/114505.html', 'http://www.zybus.com/yirentuku/114499.html', 'http://www.zybus.com/yirentuku/114497.html', 'http://www.zybus.com/yirentuku/114498.html', 'http://www.zybus.com/yirentuku/114495.html', 'http://www.zybus.com/yirentuku/114493.html', 'http://www.zybus.com/yirentuku/114492.html', 'http://www.zybus.com/yirentuku/114491.html', 'http://www.zybus.com/yirentuku/114490.html']
        # htmllist = ['http://www.zybus.com/yirentuku/77200.html',
        #             'http://www.zybus.com/yirentuku/77118.html', 'http://www.zybus.com/yirentuku/77117.html',
        #             'http://www.zybus.com/yirentuku/77116.html', 'http://www.zybus.com/yirentuku/77115.html',
        #             'http://www.zybus.com/yirentuku/77112.html', 'http://www.zybus.com/yirentuku/77119.html',
        #             'http://www.zybus.com/yirentuku/77113.html']

        for html in htmllist:
            if html == 'http://www.zybus.com/yirentuku/84105.html':
                continue
            print(html)
            urls = self.get_img_url(html)
            print(urls)

            name = self.get_name_htmls(html)
            # name = '权珉阿'
            print(name)
            # for url in urls:#在某艺人的 主页上获取他那张最大的pic 图像
            self.download_images(urls, name, dirpath)  # 保存下来
        # pass


if __name__ == '__main__':
    urls = ['http://www.zybus.com/yirentuku/list_213_18.html','http://www.zybus.com/yirentuku/list_213_10.html']

    dir = 'D:\\工作内容\\测试记录\\样本\\明星照片\\'
    for url in urls:
        Yiren = YirenSpider()
        # i = 0
        Yiren.spider(url, dir)
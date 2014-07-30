'''
Created on 28.07.2014

@author: chriad
'''
import ARTE_grabber

def test_get_json_url(soup):
    assert type(ARTE_grabber.get_json_url(soup))=='bs4.BeautifulSoup'
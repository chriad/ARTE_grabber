#!/usr/local/bin/python2.7
# encoding: utf-8
'''
ARTE_grabber -- shortdesc

ARTE_grabber is a description

It defines classes_and_methods

@author:     user_name

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import os
import logging

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
try:
    from bs4 import BeautifulSoup
except:
    print('Need Beatiful Soup')
    sys.exit(1)
    
import urllib2
    
import re
import json
import subprocess

# Setup logger

logger = logging.getLogger(name='ARTE_grabber')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(fmt)
logger.addHandler(console_handler)

__all__ = []
__version__ = 0.1
__date__ = '2014-07-28'
__updated__ = '2014-07-28'

DEBUG = 1


class CLIError(Exception):

    '''Generic exception to raise and log different fatal errors.'''

    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


def fetch_page(web_url):
    page = urllib2.urlopen(web_url, timeout=1)
    content = page.read()
    page.close()
    return content


def get_json_url(soup):
    json_tag = soup.find_all(
        'div',
        'video-container',
        arte_vp_url=re.compile('PLUS7-D'))[0]
    return json_tag.attrs['arte_vp_url']
        
def load_json_ressource(json_url):
    '''
    Retrun the content of a json file or web resource
    :param json_url: A json file or web resource
    :type json_url: str
    '''
    page = urllib2.urlopen(json_url)
    content = page.read()
    page.close()
    content = json.loads(content)
    return content

def extract_rtmp_params(json_content):
    base = json_content['videoJsonPlayer']['VSR']['RTMP_SQ_1']
    streamer = base['streamer']
    url = base['url']
    return streamer, url

def get_console_logger():
    
    logger = logging.getLogger(name='ARTE_grabber')
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)
    return logger


def extract_html_params(json_content):
    base = json_content['videoJsonPlayer']['VSR']['HTTP_MP4_SQ_1']
    url = base['url']
    return url


def call_vlc(url):
    '''
    usage: http://www.arte.tv/guide/de/051682-015/fast-die-ganze-wahrheit?autoplay=1?autoplay=1
    '''
    url = 'wrong_url'
    command = [
        'cvlc', '-v',
        url,
        '--sout=./video'+str(os.getpid())+'.mp4',
        'vlc://quit']
    try:
        logger.info('Trying vlc command: '+' '.join(command))
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=False)
    except subprocess.CalledProcessError as errorvariable:
        # Catch only this specific type of exception
        print('vlc process failed')
        logger.info('Failed command is: '+' '.join(command))
        print(errorvariable.output)
    return


def call_rtmpdump(streamer, url):
    "used with arte 7"
    command = ['rtmpdump',
               '--tcUrl',
               streamer,
               '--playpath',
               "mp4:" + url,
               '--rtmp',
               streamer + url,
               '-o',
               'video_out' + str(os.getpid())]
    print(command)
    subprocess.check_output(command, stderr=subprocess.STDOUT, shell=False)
    return


def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (
        program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by user_name on %s.

USAGE
''' % (program_shortdesc, str(__date__))    
    
    try:
        # Setup argument parser
        parser = ArgumentParser(
            description=program_license,
            formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument(
            "-v",
            "--verbose",
            dest="verbose",
            action="count",
            help="set verbosity level [default: %(default)s]")
        parser.add_argument(
            '-V',
            '--version',
            action='version',
            version=program_version_message)
        parser.add_argument('url')

        # Process arguments
        args = parser.parse_args()
        web_url = args.url

        verbose = args.verbose

        if verbose > 0:
            print("Verbose mode on")
            
        
        try:
            content = fetch_page(web_url)
        except:
            print('Internet probably disconnected')
        soup = BeautifulSoup(content)
        json_url = get_json_url(soup)
        logger.info(json_url)
        json_content = load_json_ressource(json_url) 
        
        vlc_url = extract_html_params(json_content)
        call_vlc(vlc_url)
        logger.info('Falling back on rtmp')
        #streamer, url = extract_rtmp_params(json_content)
        #call_rtmpdump(streamer, url)

        

        
        

        # do something

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        #sys.argv.append("-h")
        sys.argv.append("-v")
        #sys.argv.append("-r")
    sys.exit(main())

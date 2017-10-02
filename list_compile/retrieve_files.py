# from ftplib import FTP
import config
import os
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import requests
import shutil


WIKI_METADATA_URL = "http://download.kiwix.org/wp1/"

def ftp_main():
    # as of August 2017, this code is no longer viable; kiwix does not maintain an ftp site from which
    # to download code.  Leaving this code here in case that project is revived.
    if not os.path.exists(config.which_wiki):
        os.makedirs(config.which_wiki)
    with FTP(source_address=(config.ftp_site, config.ftp_port),
             user=config.ftp_user,
             passwd=config.ftp_pass) as ftp:
        ftp.cwd(config.which_wiki)
        all_files = ftp.nlst()
        for file in all_files:
            print ("retrieving {}".format(file))
            ftp.retrbinary('RETR {}'.format(file),
                           open(os.path.join(config.which_wiki, file), 'wb').write)

def main():
    # cribbing heavily from https://stackoverflow.com/questions/1080411/retrieve-links-from-web-page-using-python-and-beautifulsoup#1080472
    if not os.path.exists(config.which_wiki):
        os.makedirs(config.which_wiki)
    url_path = config.metadata_location + config.which_wiki
    resp = requests.get(url_path)
    http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
    html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
    encoding = html_encoding or http_encoding
    soup = BeautifulSoup(resp.content, from_encoding=encoding)
    for link in soup.find_all('a', href=True):
        if link['href'].endswith('lzma'):
            print(link['href'])
            # cribbing from https://stackoverflow.com/questions/13137817/how-to-download-image-using-requests#13137873
            lzma_resp = requests.get(url_path + link['href'], stream=True)
            if lzma_resp.status_code == 200:
                with open(config.which_wiki + "/" + link['href'], 'wb') as f:
                    lzma_resp.raw.decode_content = True
                    shutil.copyfileobj(lzma_resp.raw, f) 


if __name__ == "__main__":
    main()
import streamlit as st
import requests
import re
from bs4 import BeautifulSoup


def write_html(html):
    return st.markdown(html, unsafe_allow_html=True)


def youtube_url_validation(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match

    return youtube_regex_match


def image_validation(filename):
  image_regex = (r'(.*)(\w+)(.gif|.jpg|.jpeg|.tiff|.png)')
  image_regex_match = re.match(image_regex, filename)
  if image_regex_match:
    return image_regex_match
  return image_regex_match


def grab_image_link(link):
  if image_validation(link):
    return link
  return None


def grab_video_link(link):
  if youtube_url_validation(link):
    return link
  return None


def grab_links(status_obj):
  image_urls = []
  video_urls = []
  for media_attachment in status_obj['media_attachments']:
    p_image_url = grab_image_link(media_attachment['url'])
    if p_image_url:
      image_urls.append(p_image_url)

  soup = BeautifulSoup(status_obj['content'])
  for a_tag in soup.findAll('a'):
    p_video_url = grab_video_link(a_tag.get('href'))
    if p_video_url:
      video_urls.append(p_video_url)
  url_dict = {
      'image_urls': image_urls,
      'video_urls': video_urls
  }
  return url_dict


def download_image(link, image_name):
  img_data = requests.get(link).content
  with open(f'./{image_name}.jpg', 'wb') as handler:
      handler.write(img_data)
  return


def search(query, mt):
  return mt.timeline_hashtag(query)

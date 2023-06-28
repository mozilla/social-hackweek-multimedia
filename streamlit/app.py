from typing import List

import streamlit as st
from mastodon import Mastodon

from helpers import write_html, grab_links, search
from classifiers import classify_image, classify_video

from enum import Enum


st.set_page_config(layout="wide")


class Classes(Enum):
    ADULT_CONTENT = 'adult content'
    PORN = 'porn'
    SPOOF = 'spoof'
    MEDICAL = 'medical'
    VIOLENCE = 'violence'
    RACY = 'racy'
    WAR = 'war'
    TEXT = 'text'

    @classmethod
    def is_nsfw(cls, class_str: str) -> bool:
        return class_str in cls.get_nsfw_classes()

    @classmethod
    def get_nsfw_classes(cls) -> List:
        return [cls.ADULT_CONTENT.value, cls.RACY.value, cls.PORN]


all_classes = {
    Classes.ADULT_CONTENT.value,
    Classes.PORN.value,
    Classes.SPOOF.value,
    Classes.MEDICAL.value,
    Classes.VIOLENCE.value,
    Classes.RACY.value,
    Classes.WAR.value,
    Classes.TEXT.value
}

if 'classes' not in st.session_state:
    st.session_state['classes'] = all_classes

new_class = st.text_input('Add class')
if new_class:
    st.session_state['classes'].add(new_class)

classes = st.multiselect('Classes', st.session_state['classes'],
                         default=st.session_state['classes'])

image_threshold = st.number_input('Image threshold', value=18)
video_threshold = st.number_input('Video threshold', value=18)

content_type = st.selectbox('Content type', ['image', 'video'])

mastodon_social_feed = []
temp_mastodon_social_feed = []
MASTODON_FEED = 'MASTODON_FEED'
MASTODON_FEED_TEMP = 'MASTODON_FEED_TEMP'
SEARCH = 'search'
UNBLUR_IMAGES = 'UNBLUR_IMAGES'


Mastodon.create_app(
    'hack-posttoots',
    api_base_url='https://mastodon.social',
    scopes=['read', 'write'],
    to_file='.secrets'
)
mastodon = Mastodon(
    client_id='.secrets',
)

NUM_ITEMS = 100

with st.spinner('Loading Mastodon.social federated feed'):
    # run this only once to create the secrets file
    if MASTODON_FEED not in st.session_state:
        mastodon_social_feed = mastodon.timeline_public(only_media=True, limit=NUM_ITEMS)
        st.session_state[MASTODON_FEED] = mastodon_social_feed
        st.session_state[MASTODON_FEED_TEMP] = mastodon_social_feed.copy()
        st.session_state[SEARCH] = ''


if st.button(label='Refresh data', key='refresh'):
    mastodon_social_feed = mastodon.timeline_public(only_media=True, limit=NUM_ITEMS)
    st.session_state[MASTODON_FEED] = mastodon_social_feed
    st.session_state[MASTODON_FEED_TEMP] = mastodon_social_feed.copy()
    st.experimental_rerun()

check = st.checkbox('Unblur images')
if check:
    st.session_state[UNBLUR_IMAGES] = True
else:
    st.session_state[UNBLUR_IMAGES] = False


def render_feed_with_predictions(all_data, limit):
    data_columns = ['Post', 'Image', 'Prediction']
    all_columns = data_columns
    column_weights = [2.5, 2.5, 1]
    cols = st.columns(column_weights)

    for col, field in zip(cols, all_columns):
        col.write("**" + field + "**")

    for i, data in enumerate(all_data[0: limit]):
        cols = st.columns(column_weights)
        for j, (col, val) in enumerate(zip(cols, data)):
            content_html = data['content']
            urls = grab_links(data)
            print(f'extracted urls: {urls}')
            image_urls = urls['image_urls']
            video_urls = urls['video_urls']
            if not image_urls and not video_urls:
                continue

            scores = None
            with st.spinner('Running model'):
                if content_type == 'video' and video_urls:
                    scores = classify_video(video_urls[0], classes, video_threshold)
                elif content_type == 'image' and image_urls:
                    scores = classify_image(image_urls[0], classes, image_threshold)
            if j == 0:
                col.markdown(content_html if len(content_html) > 0 else 'No content', unsafe_allow_html=True)
            elif j == 1:
                if content_type == 'image' and image_urls:
                    should_blur = [s[0] for s in scores if s[0] in Classes.get_nsfw_classes()]
                    blur_str = 'style="filter: blur(15px);"' if (should_blur and not st.session_state[UNBLUR_IMAGES]) else ''
                    col.markdown(f'<img src={image_urls[0]} {blur_str} alt="" width="250" height="250">', unsafe_allow_html=True)
                elif content_type == 'video' and video_urls and '.mp4' in video_urls[0]:
                    should_blur = [s[0] for s in scores if s[0] in Classes.get_nsfw_classes()]
                    blur_str = 'style="filter: blur(15px);"' if (should_blur and not st.session_state[UNBLUR_IMAGES]) else ''
                    preview_url = urls['preview_urls'][0]
                    col.markdown(f'<video width="320" height="240" poster="{preview_url}" {blur_str} controls><source src="{video_urls[0]}" type="video/mp4">video</video>',
                                 unsafe_allow_html=True)
            elif j == 2:
                if scores:
                    col.write(str(scores))

        write_html('<br/>')


def render():
    with st.form(key='Search'):
        search_string = ''
        search_string = st.text_input(f'Enter text to search ({len(st.session_state[MASTODON_FEED])} posts)', search_string)
        st.session_state[SEARCH] = search_string
        corpus_submit_button = st.form_submit_button(label='Search')
        if corpus_submit_button or search_string:
            st.session_state[MASTODON_FEED_TEMP] = search(search_string, mastodon, limit=NUM_ITEMS)
        render_feed_with_predictions(st.session_state[MASTODON_FEED_TEMP], NUM_ITEMS)


render()

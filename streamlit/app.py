import streamlit as st
from mastodon import Mastodon

from helpers import write_html, grab_links, search
from classifiers import classify_image, classify_video

all_classes = {"adult content", "spoof", "medical", "violence", "racy", "war", 'politics'}
if 'classes' not in st.session_state:
    st.session_state['classes'] = all_classes

new_class = st.text_input('Add class')
if new_class:
    st.session_state['classes'].add(new_class)

classes = st.multiselect('Classes', st.session_state['classes'],
                         default=st.session_state['classes'])

image_threshold = st.number_input('Image threshold', value=18)
video_threshold = st.number_input('Video threshold', value=18)

mastodon_social_feed = []
temp_mastodon_social_feed = []
MASTODON_FEED = 'MASTODON_FEED'
MASTODON_FEED_TEMP = 'MASTODON_FEED_TEMP'
SEARCH = 'search'

st.set_page_config(layout="wide")

Mastodon.create_app(
    'hack-posttoots',
    api_base_url='https://mastodon.social',
    scopes=['read', 'write'],
    to_file='.secrets'
)
mastodon = Mastodon(
    client_id='.secrets',
)

with st.spinner('Loading Mastodon.social federated feed'):
    # run this only once to create the secrets file
    if MASTODON_FEED not in st.session_state:
        mastodon_social_feed = mastodon.timeline_public(only_media=True, limit=10)
        st.session_state[MASTODON_FEED] = mastodon_social_feed
        st.session_state[MASTODON_FEED_TEMP] = mastodon_social_feed.copy()
        st.session_state[SEARCH] = ''


if st.button(label='Refresh data', key='refresh'):
    mastodon_social_feed = mastodon.timeline_public(only_media=True, limit=10)
    st.session_state[MASTODON_FEED] = mastodon_social_feed
    st.session_state[MASTODON_FEED_TEMP] = mastodon_social_feed.copy()
    st.experimental_rerun()


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
            image_urls = urls['image_urls']
            video_urls = urls['video_urls']
            if (not image_urls and not video_urls) or len(image_urls) == 0:
                continue
            if j == 0:
                col.markdown(content_html if len(content_html) > 0 else 'No content', unsafe_allow_html=True)
            elif j == 1:
                col.markdown(f'<img src={image_urls[0]} alt="" width="250" height="250"> ', unsafe_allow_html=True)
            elif j == 2:
                with st.spinner('Running model'):
                    if image_urls:
                        scores = classify_image(image_urls[0], classes, image_threshold)
                    elif video_urls:
                        scores = classify_video(video_urls[0], classes, video_threshold)
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
            st.session_state[MASTODON_FEED_TEMP] = search(st.session_state[MASTODON_FEED], search_string)
        render_feed_with_predictions(st.session_state[MASTODON_FEED_TEMP], 10)


render()

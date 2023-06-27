import streamlit as st
from mastodon import Mastodon

from helpers import write_html, grab_links
from classifiers import classify_image, classify_video

all_classes = {"adult content", "spoof", "medical", "violence", "racy", "war", 'politics'}
if 'classes' not in st.session_state:
    st.session_state['classes'] = all_classes

new_class = st.text_input('Add class')
if new_class:
    st.session_state['classes'].add(new_class)

classes = st.multiselect('Classes', st.session_state['classes'],
                         default=st.session_state['classes'])

image_threshold = st.number_input('Image threshold', 18)
video_threshold = st.number_input('Video threshold', 18)

mastodon_social_feed = []
with st.spinner('Loading Mastodon.social federated feed'):
    Mastodon.create_app(
        'hack-posttoots',
        api_base_url='https://mastodon.social',
        scopes=['read', 'write'],
        to_file='.secrets'
    )
    mastodon = Mastodon(
        client_id='.secrets',
    )
    mastodon_social_feed = mastodon.timeline_public(only_media=True)
    st.success(f'Found {len(mastodon_social_feed)} posts!')


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
            if not image_urls and not video_urls:
                continue
            if j == 0:
                col.markdown(content_html, unsafe_allow_html=True)
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

        write_html('<hr/>')


def render(data):
    render_feed_with_predictions(data, 10)


render(mastodon_social_feed)

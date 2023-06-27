import streamlit as st
from mastodon import Mastodon

from helpers import write_html, grab_links

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
            if j == 0:
                col.markdown(content_html, unsafe_allow_html=True)
            elif j == 1:
                col.markdown(f'<img src={image_urls[0]} alt="" width="250" height="250"> ', unsafe_allow_html=True)
            elif j == 2:
                col.markdown('Not sensitive', unsafe_allow_html=True)
            # elif j == 3:
            #     col.markdown(, unsafe_allow_html=True)
        write_html('<hr/>')


def render(data):
    render_feed_with_predictions(data, 20)


render(mastodon_social_feed)
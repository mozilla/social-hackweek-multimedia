# social-hackweek-multimedia
Exploration of processing multimedia content on social networks with AI

## Detecting sensitive content
We explore flagging sensitive images and videos using zero-shot classification.

The pre-trained models we use:
- CLIP for images ([huggingface](https://huggingface.co/openai/clip-vit-large-patch14))
- X-CLIP for videos ([huggingface](https://huggingface.co/microsoft/xclip-base-patch32))

The app can load the federated timeline from Mastodon or search by tag.
It is possible to add custom text descriptions for classification. The models are universal and can be used for a variety of classificaiton and search tasks. 

<img width="1280" alt="Screenshot 2023-07-04 at 2 41 37 PM" src="https://github.com/mozilla/social-hackweek-multimedia/assets/2486505/558757e5-b03f-4c51-8a11-06fa3f3002e9">



## Running the app

### Install dependencies 
```
cd social-hackweek-multimedia/streamlit

python3 -m venv hackweek-multimedia-env
source hackweek-multimedia-env/bin/activate
pip install -r requirements.txt

# to deactivate
deactivate
```

### Run streamlit app
```
streamlit run app.py
```


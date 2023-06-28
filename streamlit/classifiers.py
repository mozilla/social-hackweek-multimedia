from PIL import Image
import av
import numpy as np
import requests
import torch
from PIL import Image
from transformers import AutoModel, \
    AutoProcessor
from transformers import CLIPProcessor, CLIPModel

np.random.seed(0)
image_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
image_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
video_processor = AutoProcessor.from_pretrained("microsoft/xclip-base-patch32")
video_model = AutoModel.from_pretrained("microsoft/xclip-base-patch32")


def classify_image(url, texts, threshold=18):
    print(f'Processing image {url}')
    image = Image.open(requests.get(url, stream=True).raw)

    inputs = image_processor(text=texts, images=image, return_tensors="pt", padding=True)

    outputs = image_model(**inputs)
    logits_per_image = outputs.logits_per_image  # this is the image-text similarity score
    # probs = logits_per_image.softmax(dim=1)  # we can take the softmax to get the label probabilities

    scores = sorted([(text, round(logit, 4))
                 for text, logit in zip(texts, logits_per_image.detach().numpy().tolist()[0])
                     if logit > threshold],
                reverse=True, key=lambda x: x[1])
    return scores


def _read_video_pyav(container, indices):
    '''
    Decode the video with PyAV decoder.
    Args:
        container (`av.container.input.InputContainer`): PyAV container.
        indices (`List[int]`): List of frame indices to decode.
    Returns:
        result (np.ndarray): np array of decoded frames of shape (num_frames, height, width, 3).
    '''
    frames = []
    container.seek(0)
    start_index = indices[0]
    end_index = indices[-1]
    for i, frame in enumerate(container.decode(video=0)):
        if i > end_index:
            break
        if i >= start_index and i in indices:
            frames.append(frame)
    return np.stack([x.to_ndarray(format="rgb24") for x in frames])


def _sample_frame_indices(clip_len, frame_sample_rate, seg_len):
    converted_len = int(clip_len * frame_sample_rate)
    end_idx = np.random.randint(converted_len, seg_len)
    start_idx = end_idx - converted_len
    indices = np.linspace(start_idx, end_idx, num=clip_len)
    indices = np.clip(indices, start_idx, end_idx - 1).astype(np.int64)
    return indices


def classify_video(url, texts, threshold):
    print(f'Processing video {url}')
    container = av.open(url)

    # sample 8 frames
    indices = _sample_frame_indices(clip_len=8, frame_sample_rate=1, seg_len=container.streams.video[0].frames)
    video = _read_video_pyav(container, indices)

    inputs = video_processor(
        text=texts,
        videos=list(video),
        return_tensors="pt",
        padding=True,
    )

    # forward pass
    with torch.no_grad():
        outputs = video_model(**inputs)

    logits_per_video = outputs.logits_per_video  # this is the video-text similarity score
    # probs = logits_per_video.softmax(dim=1)  # we can take the softmax to get the label probabilities

    scores = sorted([(text, round(logit, 4))
                 for text, logit in zip(texts, logits_per_video.detach().numpy().tolist()[0])
                     if logit > threshold],
                reverse=True, key=lambda x: x[1])

    return scores

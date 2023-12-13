import datetime
import os
import re
import collections
import typing
import bisect

import cv2
import numpy as np
import instaloader

import bot_secrets

INSTAGRAM_URL_RE = r"https://www\.instagram\.com/reel/([^/?]+)"
REEL_URL_TEMPLATE = "https://www.instagram.com/reel/{reel_id}/"


__all__ = [
    "is_reel",
    # "pause_game_full",
    "cleanup",
]


def is_reel(msg: str) -> bool:
    reel_id_arr = re.findall(INSTAGRAM_URL_RE, msg)
    return bool(reel_id_arr)


# def pause_game_dl_video(insta_reel_url: str) -> typing.Optional[str]:
#
#     reel_id_arr = re.findall(INSTAGRAM_URL_RE, insta_reel_url)
#     if not reel_id_arr:
#         return None
#
#     reel_id = reel_id_arr[0]
#
#     instagram = instaloader.Instaloader()
#     instagram.load_session_from_file(**bot_secrets.INSTA_INFO)
#
#     dl_dir = os.path.abspath(os.path.join(os.getcwd(), reel_id))
#
#     dl_res = instagram.download_post(
#         instaloader.Post.from_shortcode(instagram.context, reel_id), reel_id
#     )
#     if not dl_res:
#         return None
#
#     files = os.listdir(dl_dir)
#     video_file = [x for x in files if x.endswith(".mp4")]
#     if not video_file:
#         return None
#
#     fp_full = os.path.join(dl_dir, video_file[0])
#     return fp_full


def abs_dev(a, b):
    sub1 = a - b
    sub2 = b - a
    mask = a < b
    sub1[mask] = sub2[mask]
    return sub1


def guess_pause_frame(vid: str, top_n: int = 5) -> typing.List[str]:
    vidcap = cv2.VideoCapture(vid)
    success, image = vidcap.read()
    prev_frame_downscaled = image
    tops = collections.deque(maxlen=top_n + 1)

    i = 0
    while success:
        success, new_image = vidcap.read()
        if not success:
            continue

        curr_frame_downscaled = new_image
        diff = abs_dev(curr_frame_downscaled, prev_frame_downscaled)
        diff_index = np.sum(diff)

        if diff_index > min([x[0] for x in tops], default=0):
            bisect.insort_left(tops, (diff_index, new_image))
            if len(tops) > top_n:
                tops.popleft()

        prev_frame_downscaled = new_image
        i += 1

    paths = []
    for i, (diff_index, image) in enumerate(tops):
        fname = os.path.abspath(
            os.path.join(
                __file__,
                "..",
                "frames",
                f"{int(datetime.datetime.utcnow().timestamp())}_{len(tops) - i}.jpg",
            )
        )
        cv2.imwrite(filename=fname, img=image)  # save frame as JPEG file
        paths.append(fname)

    return paths


# def pause_game_full(insta_reel_url: str, top_n: int = 5) -> typing.List[str]:
#     video_path = pause_game_dl_video(insta_reel_url)
#     if not video_path:
#         return []
#     frames = guess_pause_frame(video_path, top_n=top_n)
#     os.remove(video_path)
#     return frames


def cleanup(paths: typing.List[str]) -> None:
    for path in paths:
        os.remove(path)
    return None

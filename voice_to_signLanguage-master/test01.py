from conf import SAMPLE_INPUTS,SAMPLE_OUTPUTS
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips
import glob, os

def _get_word_clip(token):
    token_lower = token.lower()
    # Exact name match in SAMPLE_INPUTS
    exact_path = os.path.join(SAMPLE_INPUTS, f"{token_lower}.mp4")
    if os.path.exists(exact_path):
        return VideoFileClip(exact_path)

    # Search in SAMPLE_INPUTS for case-insensitive names
    for file in glob.glob(os.path.join(SAMPLE_INPUTS, "*.mp4")):
        if token_lower == os.path.splitext(os.path.basename(file))[0].lower():
            return VideoFileClip(file)

    # Fallback to letter-based assembly from alphabet folder
    if len(token_lower) > 1:
        letter_clips = []
        for ch in token_lower:
            alpha_path = os.path.join(SAMPLE_INPUTS, "alphabets", f"{ch}.mp4")
            if os.path.exists(alpha_path):
                letter_clips.append(VideoFileClip(alpha_path))
            else:
                for fallback in glob.glob(os.path.join(SAMPLE_INPUTS, "alphabets", "*.mp4")):
                    if ch == os.path.splitext(os.path.basename(fallback))[0].lower():
                        letter_clips.append(VideoFileClip(fallback))
                        break
                else:
                    raise FileNotFoundError(f"Alphabet clip not found for character '{ch}' in {SAMPLE_INPUTS}/alphabets")

        assembled_clip = concatenate_videoclips(letter_clips, method='compose')
        # Optional cache write to input folder for performance:
        try:
            assembled_clip.write_videofile(exact_path, verbose=False, logger=None)
        except Exception:
            pass
        return assembled_clip

    raise FileNotFoundError(f"Word clip not found for token '{token}' in {SAMPLE_INPUTS}")


def generateclip(s):
    tokens = s.strip().split()
    if not tokens:
        raise ValueError("Input sentence is empty")

    clips = []
    for token in tokens:
        clips.append(_get_word_clip(token))

    if not clips:
        raise ValueError("No clips found for input sentence")

    final_clip = concatenate_videoclips(clips, method='compose')
    os.makedirs(SAMPLE_OUTPUTS, exist_ok=True)
    output_path = os.path.join(SAMPLE_OUTPUTS, "clipg.mp4")
    final_clip.write_videofile(output_path)
    return output_path

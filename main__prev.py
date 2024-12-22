import cv2
from PIL import Image
import imagehash
from os import mkdir, listdir
from subprocess import call
import re


INTERVAL = 15

def is_similar(img1, img2, cutoff = 2): # maximum bits that could be different between the hashes. 
    hash0 = imagehash.average_hash(Image.fromarray(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB))) 
    hash1 = imagehash.average_hash(Image.fromarray(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB))) 

    if hash0 - hash1 < cutoff:
        return True
    else:
        return False

    
def extract_frames(video_path, output_path, interval):
    vidcap = cv2.VideoCapture(video_path)
    fps = int(vidcap.get(cv2.CAP_PROP_FPS))

    success, prev_frame = vidcap.read()
    count = 0

    print("[ info ] Extracting frames.")

    while success:
        if count % (interval * fps) == 0:
            success, current_frame = vidcap.read()
            if not is_similar(prev_frame, current_frame):
                cv2.imwrite(f"{output_path}/frame{count // (interval * fps)}.jpg", current_frame)
            prev_frame = current_frame
        else:
            success = vidcap.grab()
        count += 1

    vidcap.release()

def fetch_video(V_url=None, V_name=None):

    if not V_url and not V_name:
        V_url = input("Enter video url : ")
        V_name = input("Enter a name : ")
    
    # make and chANGE directory
    mkdir(V_name)
    mkdir(V_name + "/frames")

    call(f"yt-dlp -f 'bestvideo[ext=mp4]/mp4' {V_url}", shell=True)

    # rename video file
    call(f"mv *.mp4 {V_name}/{V_name}.mp4", shell=True)

    return V_name, V_name + "/" + V_name + ".mp4", 


def sort_key(frame_name):
    return int(re.search(r'\d+', frame_name).group())


def generate_pdf(image_dir, fname):
    print("[ info ] Genearting pdf.")
    # Directory containing images

    images_list = sorted(listdir(image_dir), key=sort_key)
    images = [
    Image.open(image_dir + "/" + f)
        for f in images_list
    ]
        
    images[0].save(
        fname, "PDF" ,resolution=100.0, save_all=True, append_images=images[1:]
    )

    print(f'PDF file "{fname}" created successfully.')

# Usage example:
working_dir, video_path = fetch_video()
output_path_frames = working_dir + "/frames"

extract_frames(video_path, output_path_frames, interval=INTERVAL)


generate_pdf(working_dir + "/frames", working_dir + "/" + working_dir + ".pdf")

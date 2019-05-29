import os
import cv2
import time
import subprocess

def format_timedelta(seconds):
    hours = seconds // 3600
    minutes = (seconds // 60) - (hours * 60)
    return "_%02d_%02d_%06.3f" %(hours, minutes, seconds - (minutes * 60) - (hours * 3600))
    # return "%02d:%02d:%02.3f" %(hours, minutes, seconds - (minutes * 60) - (hours * 3600))

def extractImages(pathIn, pathOut):
    try:
        os.mkdir(pathOut)
    except Exception as FileExistsError:
        pass
    except Exception as e:
        return

    vidcap = cv2.VideoCapture(pathIn)
    fps = vidcap.get(cv2.CAP_PROP_FPS) # fps = 15
    success, image = vidcap.read()

    count = 0
    # skip by 300ms
    time_step = 300 / 1000
    last_time = 0

    while(vidcap.isOpened()):
        count += 1 # frame by frame
        frame_exists, curr_frame = vidcap.read()
        if frame_exists:
            seconds = count/fps
            # skip by 300ms, about 4000 image for one 24min video
            if seconds - last_time > time_step:
                last_time = seconds
                str_time = format_timedelta(seconds)

                # Cut from (0, 184) -> (352, 264)
                x, y = 0, 176
                w, h = 352, 254
                text_frame_crop = curr_frame[y:y+h, x:x+w]

                # # for test
                # if not(64 < seconds < 74):
                #     continue

                print('Save frame at', str_time)
                cv2.imwrite(pathOut + "\\frame%s.jpg" % str_time, text_frame_crop)

        else:
            break

    vidcap.release()


def ftime(t):
    return time.strftime("%b-%d-%y %H:%M:%S", time.localtime(t))

def format_relate_time(s):
    h  = int(s / 3600)
    m  = int(( s - h * 60) / 60)
    ss = s - h * 60 - m * 60
    return "%02d:%02d:%s" %(h, m, ss)

def run(cmd, callback=None):
    TIME = time.time()
    print("[START COMMMAND]start at:", ftime(TIME))
    print("[CMD]", cmd)
    result = subprocess.call(cmd, shell=True)
    ENDTIME = time.time()
    print("[END COMMMAND]start at: %s  ending at: %s  dur: %s\n\n" %(ftime(TIME), ftime(ENDTIME),
        format_relate_time(ENDTIME-TIME)))
    return result

if __name__ == '__main__':
    import sys
    for flv_filename in [n for n in sorted(os.listdir(".")) if n.lower().endswith(".flv")]:
        mp4_filename = flv_filename.replace(".flv", ".mp4")
        if not os.path.exists(mp4_filename):
            run(r'''ffmpeg -i %s %s''' % (flv_filename, mp4_filename))

        output_path = "output_" + mp4_filename
        print("output_path:", output_path)
        if not os.path.exists(output_path):
            print(output_path, "not exists")
            try:
                os.mkdir(output_path)
            except Exception as e:
                pass
            
            extractImages(mp4_filename, output_path)

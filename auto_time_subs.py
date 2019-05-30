from collections import OrderedDict
import json
import traceback
import os
import sys
from difflib import SequenceMatcher


def string_similarity(str1, str2):
    # return SequenceMatcher(None, str1, str2).ratio()
    
    str1_l = "".join(sorted([c for c in str1]))
    str2_l = "".join(sorted([c for c in str2]))
    return SequenceMatcher(None, str1_l, str2_l).ratio()

def test_string_similarity():
    str1 = "think that's a safe bet\\n\u6211\u60f3\u90a3\u6837\u5e94\u8be5\u4e07\u65e0\u4e00\u5931"
    str2 = "I think thats a safe bet.\\n\u6211\u60f3\u90a3\u6837\u5e94\u8be5\u4e07\u65e0\u4e00\u5931"
    str3 = "Royal guard! No-one=moves\\n\u7687\u5bb6\u536b\u5175\u641c\u67e5\u8c01\u90fd\u4e0d\u51c6\u52a8"
    str4 = "Oh, yes my Lord, I value my-life\\n\u5662\u5f53\u7136\u6bbf\u4e0b\u6211\u5f88\u73cd\u60dc\u81ea\u5df1\u751f\u547d\u7684"
    str5 = "\u5662\u5f53\u7136\u6bbf\u4e0b\\nLord, I value my\\n\u6211\u5f88\u73cd\u60dc\u81ea\u5df1\u751f\\n\uffe5\u547d\u7684"
    str6 = "\u4f5c\u4e8b"
    str7 = "\u4e00"
    print(string_similarity(str1, str2))
    print(string_similarity(str2, str3))
    print(string_similarity(str3, str4))
    print(string_similarity(str4, str5))
    print(string_similarity(str5, str6))
    print(string_similarity(str6, str7))

def remove_no_chinese(string):
    return string

def time_the_sub(filepath=""):
    if not os.path.exists(filepath):
        print("filepath not exists", filepath)
        return

    with open(filepath, "r") as f:
        data = f.read()

    data = json.loads(data)
    sub_count = len(data)
    if not sub_count:
        print("file has no content", filepath)
        return

    data.append([data[sub_count-1][0], "", 0])

    current_sub = ""
    current_sub_probability = 0
    start_time = ""

    for index in range(sub_count + 1):
        filename, content, probability = data[index]

        frame_time = filename.replace("frame_", "").replace("_", ":").replace(".jpg", "")

        # 1.Take Probability filter, value > 0.6
        # 2.Compare how similar is current sub and next sub
        #   Apply the filter which value > 0.6
        # if string_similarity(content, content_n) < 0.6 or probability < 0.6:
        if string_similarity(current_sub, content) < 0.6 or probability < 0.6:

            if current_sub == "":
                # 2.1 Found New Sub
                current_sub = content
                start_time = frame_time
            else:
                # 2.2 Break The Track, Store Cache As Sub
                print(start_time, end_time, current_sub)
                current_sub = content
                current_sub_probability = probability
                start_time = frame_time

            continue

        # 3.Choice The sub with Highest probability
        if probability > current_sub_probability:
            current_sub = content

        end_time = frame_time

if __name__ == '__main__':
    time_the_sub(r"result_output_32.mp4.json")
    # test_string_similarity()

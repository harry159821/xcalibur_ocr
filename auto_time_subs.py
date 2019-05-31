from collections import OrderedDict
import json
import traceback
import os
import sys
from difflib import SequenceMatcher
import pathlib

ass_file_header = r'''
[Script Info]
Title: Default Aegisub file
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1440
PlayResY: 1152
Aegisub Video Aspect Ratio: c1.250000
Video Aspect Ratio: 0

[Aegisub Project Garbage]
Audio File: Xcalibur.Episode.20.mp4
Video File: Xcalibur.Episode.20.mp4
Video AR Mode: 4
Video AR Value: 1.250000
Video Zoom Percent: 0.500000
Scroll Position: 252
Active Line: 263
Video Position: 30211

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: 神秘岛,微软雅黑,50,&H00FFFFFF,&H000000FF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,2,2,2,20,20,30,1
Style: 神秘岛-片头,汉仪瘦金书简,50,&H00FFFFFF,&H000000FF,&H00000000,&H50000000,-1,0,0,0,100,100,0,0,1,2,4,2,20,20,20,1
Style: 神秘岛-剧名,方正启体简体,85,&H002D88C6,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,4,4,8,20,20,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:02.13,0:00:05.60,神秘岛-片头,,0,0,0,,{\fad(500,500)\pos(720,1050)}翻译：英语辅导频道\N\N输入/时间轴/压制：harry159821/黑月
Dialogue: 0,0:00:06.00,0:00:09.61,神秘岛-片头,,0,0,0,,{\fad(200,1000)\pos(720,1050)}校对：
Dialogue: 0,0:00:00.00,0:00:53.53,神秘岛,,0,0,0,Banner;6;0;50, {\an8}{\fn幼圆}谨以此片追忆逝去的童年，如果你也有这样的童年的话欢迎加入我们的贴吧"神剑传奇"。本作品之片源来自互联网，版权归原公司所有。任何组织和个人不得公开传播或用于任何商业盈利用途，一切后果由该组织或个人承担！制作者不承担任何法律及连带责任！请自觉于下载后24小时内删除。如果喜欢本片，请购买正版！
Dialogue: 0,0:23:11.86,0:23:15.86,神秘岛-片头,,0,0,0,,{\fad(500,500)\pos(720,1050)}翻译：英语辅导频道\N\N输入/时间轴/压制：harry159821/黑月
Dialogue: 0,0:23:15.86,0:23:19.86,神秘岛-片头,,0,0,0,,{\fad(200,1000)\pos(720,1050)}校对：
Dialogue: 0,0:01:01.06,0:01:04.93,神秘岛-剧名,,0,0,0,,{\fad(500,600)\frz0}第？集 '''

# Dialogue: 0,0:01:06.86,0:01:09.66,神秘岛,,0,0,0,,阿图斯国王万岁\NLong live king Arthus


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

    file_p = pathlib.Path(filepath)
    filename = file_p.stem

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
    end_time = ""
    ass_file_content = ass_file_header

    for index in range(sub_count + 1):
        framename, content, probability = data[index]
        frame_time = framename.replace("frame_", "").replace("_", ":").replace(".jpg", "")

        # 1.Take Probability filter, value > 0.6
        # 2.Compare how similar is current sub and next sub
        #   Then Apply the filter which value > 0.6
        if string_similarity(current_sub, content) < 0.6 or probability < 0.6:

            if current_sub == "":
                # 3.Found First Sub
                current_sub = content
                start_time = frame_time
                end_time = frame_time
            else:
                # 4.Break The Track, Store Cache As Sub
                print(start_time, end_time, current_sub)
                sub_content = "\nDialogue: 0,%s,%s,神秘岛,,0,0,0,,%s" %(start_time[:-1], end_time[:-1], current_sub)
                ass_file_content += sub_content

                # Reset Variables
                current_sub = content
                current_sub_probability = probability
                start_time = frame_time                

            continue

        # 5.Choice The Sub Who Have Highest probability
        if probability > current_sub_probability:
            current_sub = content
            current_sub_probability = probability

        end_time = frame_time

    with open(filename + ".ass", 'w') as f:
        f.write(ass_file_content)

if __name__ == '__main__':
    for result in [
        "result_output_32.mp4.json",
        "result_output_33.mp4.json",
        "result_output_34.mp4.json",
        "result_output_35.mp4.json",
        "result_output_36.mp4.json",
        "result_output_37.mp4.json",
        "result_output_38.mp4.json",
        "result_output_39.mp4.json",
        "result_output_40.mp4.json",
    ]:
        time_the_sub(result)
    # test_string_similarity()

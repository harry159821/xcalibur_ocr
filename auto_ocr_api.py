from aip import AipOcr
import os
import sys
import traceback
import time
from collections import OrderedDict
import json


""" APPID AK SK From https://ai.baidu.com/docs#/OCR-API/e1bd77f3 """
from config import *

import cv2
print(cv2.__version__)

def processOcr(pathOut):
    # pathOut = 'output_33.mp4'

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    options = {
        'detect_direction': 'false',
        'probability': 'false',
        'detect_language': 'false',
        'language_type':'CHN_ENG'
    }

    options = {
        'probability': 'true',
        'detect_direction':'true',
        'language_type':'CHN_ENG'
    }

    def get_file_content(filePath):
        with open(filePath, 'rb') as (fp):
            return fp.read()

    def ftime(t):
        return time.strftime("%b-%d-%y %H:%M:%S", time.localtime(t))

    # result_json = OrderedDict()
    result_json = []
    failed_json = []
    for filename in sorted(os.listdir(pathOut)):
        TIME = time.time()

        wordResult = ""
        try:
            filepath = os.path.join(pathOut, filename)

            image = get_file_content(filepath)

            try_count = 0
            for index in range(20):
                try:
                    result = client.basicGeneral(image, options)
                    # result = client.basicAccurate(image, options)
                    break
                except Exception as e:
                    try_count = index
                    print("Failed, try again", try_count, e)
                    time.sleep(5)

            if try_count >= 18:
                failed_json.append(filename)
                continue

            # print("ocr result:", result)
            
            '''
            {
                'log_id': 72640784816326460,
                'direction': 0,
                'words_result_num': 2,
                'words_result': [
                    {
                        'probability':
                        {
                            'variance': 0.003748,
                            'average': 0.966516,
                            'min': 0.80748
                        },
                        'words': 'I mean no offence, your Lordship.'
                    },
                    {
                        'probability':
                        {
                            'variance': 3e-06,
                            'average': 0.99889,
                            'min': 0.994902
                        },
                        'words': '我无意冒犯您殿下'
                    }
                ]
            }
            '''

            if 'words_result' not in result:
                continue

            wordResultList = result['words_result']
            if not len(wordResultList):
                continue

            wordResult = r"\n".join(d['words'] for d in wordResultList)
            probability_sum = sum([wordResult['probability']['average'] for wordResult in wordResultList])
            probability = probability_sum / len(wordResultList)
            
            # result_json[filename] = wordResult
            result_json.append([filename, wordResult, probability])

        except Exception as e:
            traceback.print_exc()
            break

        print(filepath, wordResult)


    with open('result_%s.json' % pathOut, 'w') as f:
        f.write(json.dumps(result_json))

    with open('result_%s_failed.json' % pathOut, 'w') as f:
        f.write(json.dumps(failed_json))

if __name__ == '__main__':
    for pathOut in [
        'output_40.mp4',
    ]:
        processOcr(pathOut)

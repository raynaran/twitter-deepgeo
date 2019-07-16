#!//usr/bin/env python
"""
Description: 
    Download tweets using tweet ID, downloaded from https://noisy-text.github.io/files/tweet_downloader.py

Usage example (in linux):
    clear;python tweet_downloader.py --credentials ../data/credentials.txt --inputfile ../data/input.tids

Inputfile contains training/validation data whose first column is tweetID

credentials.txt stores the Twitter API keys and secrects in the following order:
consumer_key
consumer_secret
access_token
access_token_secret

Required Python library: 
    ujson, twython and twokenize (https://github.com/myleott/ark-twokenize-py)

An example output with whitespace tokenised text and tweet id in JSON format
    {"text":"@SupGirl whoaaaaa .... childhood flashback .","id_str":"470363741880463362"}
"""

try:
    import ujson as json
except ImportError:
    import json
import sys
import time
import argparse
from twython import Twython, TwythonError
from collections import OrderedDict

MAX_LOOKUP_NUMBER = 100
SLEEP_TIME = 15 + 1
twitter = None
arguments = None
dic_list = None


def init():
    global twitter, arguments, dic_list

    parser = argparse.ArgumentParser(description="A simple tweet downloader for WNUT-NORM shared task.")
    parser.add_argument('--credentials', type=str, required=True, help='''\
        Credential file which consists of four lines in the following order:
        consumer_key
        consumer_secret
        access_token
        access_token_secret
        ''')
    parser.add_argument('--inputfile', type=str, required=True, help='Input file one tweet id per line')
    arguments = parser.parse_args()

    credentials = []
    with open(arguments.credentials) as fr:
        for l in fr:
            credentials.append(l.strip())
    twitter = Twython(credentials[0], credentials[1], credentials[2], credentials[3])

    dic_list = []
    with open(arguments.inputfile) as fr:
        for l in fr:
            jobj = json.loads(l.strip())
            dic_list.append(jobj)


def download():
    global twitter, arguments, dic_list

    with open(arguments.inputfile + ".data.json", "w") as dw, open(arguments.inputfile + ".label.json", "w") as lw:
        max_round = len(dic_list) // MAX_LOOKUP_NUMBER + 1

        for i in range(max_round):
            dics = dic_list[i * MAX_LOOKUP_NUMBER: (i + 1) * MAX_LOOKUP_NUMBER]
            label_dic = {item['tweet_id']: item for item in dics}
            tids = [dic['tweet_id'] for dic in dic_list[i * MAX_LOOKUP_NUMBER: (i + 1) * MAX_LOOKUP_NUMBER]]
            time.sleep(SLEEP_TIME)

            try:
                jobjs = twitter.lookup_status(id=tids)
            except TimeoutError as e:
                print(str(e))
                print(f'tweet {i * MAX_LOOKUP_NUMBER} to {(i + 1) * MAX_LOOKUP_NUMBER} were skipped.')
            else:
                for jobj in jobjs:
                    dw.write(json.dumps(jobj))
                    dw.write("\n")
                    lw.write(json.dumps(label_dic[jobj['id_str']]))
                    lw.write("\n")


def main():
    init()
    download()


if __name__ == "__main__":
    main()

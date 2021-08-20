from flask import Flask, render_template, request, redirect
import requests
import glob
import base64
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import time
import multiprocessing

app = Flask(__name__)

def signal_handler(signum, frame):
    raise Exception("Timed out!")

@app.route('/')
def form():
    return render_template('form-iframe.html')


@app.route('/verify', methods=['POST', 'GET'])
def verify():
    if request.method == 'POST':
        name = request.form['val1']

        ## DeepFace API goes here

        url = "http://192.168.0.232:5000/analyze"
        IGusername = name.strip()


        ## Directory where your script is located here

        directory = f"/home/odin/dev/instagram-emotion-x/{IGusername}/"


        ## Maximum number of seconds to fetch IG pictures

        fetchTimeout = int('130')

        ## Don't forget to pipe output to z.log if you want an interactive browser output

        print(f"[1/4]Fetching IG data for {IGusername}...")
        def bar():
            os.system(
                f"instaloader {IGusername} --login bellvuedata --password p@ssw0rd --no-videos --no-video-thumbnails --no-metadata-json --no-compress-json")

        p = multiprocessing.Process(target=bar)
        p.start()
        p.join(fetchTimeout)
        if p.is_alive():
            print("[!]Stopping media download")
            p.terminate()
            p.join()


        myfiles = glob.glob(f"{directory}*.jpg")

        f = open('moodgram.csv', 'w')
        f.write('time,mood')
        f.write('\n')
        f.close()

        print("[2/4]Contacting DeepFace API...")
        for file in myfiles:
            myfileSplit = file.split('/')
            mySplitDate = myfileSplit[6].split('-')
            mySplitDateYear = mySplitDate[0]
            mySplitDateMonth = mySplitDate[1]

            with open(fr"{file}", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())

            enc_string = encoded_string.decode('utf-8').strip()

            payload = json.dumps({
                "img": [
                    f"data:image/jpeg;base64,{enc_string}"
                ]
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            ## Using try for no face match

            try:
                DeepFaceJson = response.json()
                DominantRaw = DeepFaceJson['instance_1']['dominant_emotion']
                myEmotion = DominantRaw.replace('fear', '-2').replace('angry', '-2').replace('disgust', '-1').replace(
                    'sad', '-1').replace('neutral', '0').replace('surprise', '1').replace('happy', '2')
                f = open('moodgram.csv', 'a')
                f.write(f'{mySplitDateMonth}/{mySplitDateYear},{myEmotion}')
                f.write('\n')
                f.close()
            except Exception:
                pass


        print("[3/4]Performing Pandas plotting...")
        df = pd.read_csv('moodgram.csv', sep=',')
        df.plot.line(x='time', y='mood', label=f"Mood/{IGusername}")

        fig = plt.gcf()
        fig.set_size_inches(20, 5)
        fig.savefig('moodgram.png', dpi=80, transparent=True)
        os.system('cp moodgram.png static')
        time.sleep(3)
        print("[4/4]Finished")
        return redirect(f"/user/{name}")


@app.route('/user/<name>')
def user(name):
    return render_template('chart.html')

app.run(host='0.0.0.0', port=4444)

## Hosting on all network interfaces on port 80

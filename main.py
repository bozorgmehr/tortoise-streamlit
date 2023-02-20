import streamlit as st
import requests
import time
from tempfile import NamedTemporaryFile

API_KEY = str(st.secrets["SIEVE_API_KEY"])

st.title("Voice Cloner using Tortoise-TTS")
st.markdown('Built by [Gaurang Bharti](https://twitter.com/gaurang_bharti) powered by [Sieve](https://www.sievedata.com)')


st.write("To use, simply upload an audio sample of someone's voice - at least 10-15 seconds long - and enter what you'd like their voice to say in the text box")


def send_to_transfersh(file, clipboard=True):
    url = 'https://transfer.sh/'
    file = {'{}'.format(file): open(file, 'rb')}
    response = requests.post(url, files=file)
    download_link = response.content.decode('utf-8')

    return download_link

def upload_local(path):
    link = (send_to_transfersh(path))
    return link

def check_status(url, interval, job_id):
    finished = False
    headers = {
        'X-API-Key': API_KEY
        }
    while True:
        response = requests.get(url, headers=headers)
        data = response.json()['data']
        for job in data:
            if job['id'] == job_id:
               
                if job['status'] == 'processing':
              
                    time.sleep(interval)
                if job['status'] == 'finished':
                   
                    finished = True
                    return finished
                if job['status'] == 'error':
                    st.error("An error occured, please try again. If the error persists, please inform the developers.")
                    print(job['error'])
                    return job['error']

def fetch_video(job_id):
    url = f"https://mango.sievedata.com/v1/jobs/{job_id}"
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    }
    response = requests.get(url, headers = headers)
    data = response.json()
    url = data['data'][0]['url']
    return url

def send_data(audio_link, text, name):
    audio_link = audio_link.split("\n")
    url = "https://mango.sievedata.com/v1/push"
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
    } 
    data = {
        "workflow_name": name,
        "inputs": {
            "audio": {
                "url": audio_link[0]
                },
            "text": text
            }
        }
    try:
        response = requests.post(url, headers=headers, json=data)
        if ('id') not in response.json():
            st.error(response.json()['description'])
            return False
        return (response.json()['id'])
    except Exception as e:
        return (f'An error occurred: {e}')

#Streamlit App

audio_in = st.file_uploader("Audio Upload (.wav only)", type='.wav')

text_in = st.text_input('Text input')

workflow_name = "custom_tortoise_tts"

if st.checkbox("Noisy input audio? Check this to improve voice quality using FullSubNet (might be slower)"):
    workflow_name = "custom_fullsubnet_tortoise"

button1 = st.button("Clone Voice")

if st.session_state.get('button') != True:

    st.session_state['button'] = button1

if st.session_state['button'] == True:

    if audio_in:
        with NamedTemporaryFile(dir='.', suffix='.wav', delete=False) as f:
            f.write(audio_in.getbuffer())
            audio_url = upload_local(f.name)
            f.close()
        
    job = send_data(audio_url, text_in, workflow_name)
    if job:
        with st.spinner("Processing video"):
            status = check_status('https://mango.sievedata.com/v1/jobs', 5, str(job))
            if status == True:
                audio = fetch_video(job)
                st.audio(audio)
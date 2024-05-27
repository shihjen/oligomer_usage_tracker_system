# load the required dependencies
import streamlit as st
from time import sleep
from navigation import make_sidebar
import pickle
from pathlib import Path
import streamlit_authenticator as stauth

make_sidebar()


st.title(':blue[Welcome to BCEAD Oligomer Usage Tracker System]')

st.markdown('### Please log in to continue...')

names = ['shih jen', 'Chris Sham']
usernames = ['jen', 'chrissham']
file_path = Path(__file__).parent / 'hashed_pw.pkl'
with file_path.open('rb') as file:
    hashed_passwords = pickle.load(file)

credentials = {
    "usernames":{
        usernames[0]:{
            "name":names[0],
            "password":hashed_passwords[0]
            },
        usernames[1]:{
            "name":names[1],
            "password":hashed_passwords[1]
            }            
        }
    }

authenticator = stauth.Authenticate(credentials, 'oligo_dashboard', 'abcdef', cookie_expiry_days=0)

name, authentication_status, username = authenticator.login('main')


if authentication_status == False:
    st.error('Username/password is incorrect')
if authentication_status == None:
    st.warning('Please enter your username and password')
if authentication_status:
        st.session_state.logged_in = True
        st.success('Logged in successfully!')
        sleep(0.5)
        st.switch_page('pages/Home.py')

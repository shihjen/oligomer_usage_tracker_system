# load the required dependencies
import pickle
from pathlib import Path

import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher

names = ['shih jen','Chris Sham']
usersnames = ['jen', 'chrissham']
passwords = ['xxx', 'xxx']

hasher = Hasher(passwords)
hashed_passwords = hasher.generate()


file_path = Path(__file__).parent / 'hashed_pw.pkl'
with file_path.open('wb') as file:
    pickle.dump(hashed_passwords, file)
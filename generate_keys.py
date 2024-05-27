# load the required dependencies
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher

names = ['shih jen','Chris Sham']
usersnames = ['jen', 'chrissham']
passwords = ['xxx', 'xxx']           # passwords have been overwrite after hashing

# hash the passwords
hasher = Hasher(passwords)
hashed_passwords = hasher.generate()

# export the hashed password in pickle file
file_path = Path(__file__).parent / 'hashed_pw.pkl'
with file_path.open('wb') as file:
    pickle.dump(hashed_passwords, file)
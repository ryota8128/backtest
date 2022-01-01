#12/25 16:43
#from typing import Container
import streamlit as st
from datetime import date
from step import *
import pandas as pd

pd.options.display.float_format = '{:.2f}'.format
def init():
    if "get_data_error" not in st.session_state:
        st.session_state.get_data_error = False
    


def main():
    
    init()
    
    if "step" not in st.session_state:
        st.session_state.step = 0 
        #st.session_state.num = 0
        
    
    leftbar()
    step2func = {0:step0, 1:step1, 2:step2, 3:step3}


    func = step2func[st.session_state.step]
    content1 = st.empty()
    content2 = st.empty()
    content3 = st.empty()
    func(content1, content2, content3)










 


    



    












if __name__ == "__main__":
    main()


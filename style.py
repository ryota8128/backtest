import streamlit as st

def get_style(key):
    style_dic = {"B_2_size" :"""
        <style>
        div.stButton > button:last-child {
            height:42px;
            padding: 10px;
        }
        </style>"""}

    st.markdown(style_dic[key], unsafe_allow_html=True)

    return 

import streamlit as st

if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'page1'


def goto_page_1():
    st.session_state['current_page'] = 'page1'


def goto_page_2():
    st.session_state['current_page'] = 'page2'


def render_page_1():
    st.write('Page 1!')
    st.button(label='go to page 2', on_click=goto_page_2)


def render_page_2():
    st.write('Page 2!')
    st.button(label='go to page 1', on_click=goto_page_1)


if st.session_state['current_page'] == 'page1':
    print('render page 1!')
    render_page_1()
else:
    render_page_2()

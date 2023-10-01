import streamlit as st

st.title("Radio Buttons, Checkboxes and Buttons")

page_names = ['Checkbox', 'Button', 'Insert']
page = st.radio('Navigation', page_names)
st.write("**The variable 'page' returns:**", page)

if page == 'Checkbox':
    st.subheader('Welcome to the Checkbox page!')
    st.write("Nice to see you! :wave:")
    check = st.checkbox("Click here")
    st.write('State of the checkbox:', check)

    if check:
        nested_btn = st.button("Button nested in Checkbox")

        if nested_btn:
            st.write(":cake:"*20)
elif page == 'Button':
    st.subheader("Welcome to the Button page!")
    st.write(":thumbsup:")

else:
    st.subheader("Welcome to the Insert page!")
    txt = st.text_input('asda')
    if txt:
        nested_btn = st.button("Click to print")
        if nested_btn:
            st.write(txt)

            nested_btn2 = st.button("Click to print again")
            if nested_btn2:
                st.write(txt+'__')

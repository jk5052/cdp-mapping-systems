import streamlit as st

st.title("🧪 Test App")
st.write("If you can see this, Streamlit is working!")

if st.button("Click me!"):
    st.success("Button clicked! Everything is working.")

st.write("Current URL should be: http://localhost:8505")

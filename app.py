import streamlit as st
import tools
from tools.fetch_data import Anazlyze_stock

st.title("Stock Analysis bot")
st.write("A Bot that assists your financial journey with the power of the Internet and LLMs")

query = st.text_input('Input your investment related query:') 

Enter=st.button("Enter")
clear=st.button("Clear")

if clear:
    print(clear)
    st.markdown(' ')

if Enter:
    import time
    with st.spinner('Collecting and Analysing the data... Please hold'):
        out=Anazlyze_stock(query)
    st.success('Done!')
    st.write(out)

# import streamlit as st

# st.title("ChatGPT-like clone")

# client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# if "openai_model" not in st.session_state:
#     st.session_state["openai_model"] = "gpt-3.5-turbo"

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# if prompt := st.chat_input("What is up?"):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     with st.chat_message("assistant"):
#         stream = client.chat.completions.create(
#             model=st.session_state["openai_model"],
#             messages=[
#                 {"role": m["role"], "content": m["content"]}
#                 for m in st.session_state.messages
#             ],
#             stream=True,
#         )
#         response = st.write_stream(stream)
#     st.session_state.messages.append({"role": "assistant", "content": response})

# import streamlit as st
# import tools
# from tools.fetch_data import Anazlyze_stock

# st.title("Stock Analysis bot")
# st.write("This bot scraps and gathers real time stock realted information and analyzes it using LLM")

# query = st.text_input('Input your investment related query:') 

# Enter=st.button("Enter")
# clear=st.button("Clear")

# if clear:
#     print(clear)
#     st.markdown(' ')

# if Enter:
#     import time
#     with st.spinner('Gathering all required information and analyzing. Be patient!!!!!'):
#         out=Anazlyze_stock(query)
#     st.success('Done!')
#     st.write(out)
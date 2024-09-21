import streamlit as st
import openai

st.title("Hody - Your Reflective Journaling Companion")

# Initialize session state variables
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
    st.session_state.user_input = ''

# Function to get OpenAI response
def get_openai_response(conversation):
    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=conversation,
        max_tokens=150,
        temperature=0.7,
        n=1,
    )
    return response['choices'][0]['message']['content'].strip()

# API Key input
st.sidebar.header("API Key Required")
api_key_input = st.sidebar.text_input(
    "Enter your OpenAI API key:",
    type="password",
    placeholder="sk-...",
    help="You can get your API key from https://platform.openai.com/account/api-keys",
)

if api_key_input:
    st.session_state.api_key = api_key_input
    openai.api_key = st.session_state.api_key
elif st.session_state.api_key:
    openai.api_key = st.session_state.api_key
else:
    st.warning("Please enter your OpenAI API key to use the app.")
    st.stop()

# Initial system prompt
system_prompt = {
    "role": "system",
    "content": (
        "You are Hody, a compassionate journaling assistant that helps users reflect deeply "
        "on their thoughts without jumping to solutions. Your responses should make the user "
        "feel heard and gently encourage deeper exploration."
    )
}

# Initialize conversation
if not st.session_state.conversation:
    st.session_state.conversation.append(system_prompt)
    st.session_state.conversation.append({
        "role": "assistant",
        "content": "What is on your mind today?"
    })

# Display conversation history
for message in st.session_state.conversation[1:]:
    if message['role'] == 'assistant':
        st.markdown(f"**Hody:** {message['content']}")
    elif message['role'] == 'user':
        st.markdown(f"**You:** {message['content']}")

# User input area
user_input = st.text_area("Your Response:", value=st.session_state.user_input, height=150)

# Action buttons
col1, col2 = st.columns(2)
with col1:
    go_deeper = st.button("Go Deeper")
with col2:
    finish_entry = st.button("Finish Entry")

# Handle "Go Deeper" action
if go_deeper and user_input.strip() != '':
    # Append user's message
    st.session_state.conversation.append({"role": "user", "content": user_input})
    st.session_state.user_input = ''

    # Get Hody's response
    try:
        response = get_openai_response(st.session_state.conversation)
    except openai.error.AuthenticationError:
        st.error("Invalid API key. Please check your OpenAI API key and try again.")
        st.stop()

    # Append Hody's response
    st.session_state.conversation.append({"role": "assistant", "content": response})

# Handle "Finish Entry" action
elif finish_entry and user_input.strip() != '':
    # Append user's message
    st.session_state.conversation.append({"role": "user", "content": user_input})
    st.session_state.user_input = ''

    # Prepare summary prompt
    summary_prompt = [
        {
            "role": "system",
            "content": (
                "You are Hody, a compassionate assistant. Summarize the user's reflections and "
                "highlight any key insights in a brief manner."
            )
        }
    ]
    # Include only user's messages for summary
    user_messages = [msg for msg in st.session_state.conversation if msg['role'] == 'user']
    summary_prompt.extend(user_messages)

    # Get summary from OpenAI
    try:
        summary = get_openai_response(summary_prompt)
    except openai.error.AuthenticationError:
        st.error("Invalid API key. Please check your OpenAI API key and try again.")
        st.stop()

    # Display summary
    st.markdown("### Summary and Key Insights")
    st.write(summary)

    # Reset for new entry
    st.session_state.conversation = []
    st.session_state.user_input = ''

# Update user input in session state
st.session_state.user_input = user_input

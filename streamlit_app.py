import streamlit as st
import openai

# Set your OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("Hody - Your Reflective Journaling Companion")

def get_openai_response(conversation):
    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=conversation,
        max_tokens=150,
        temperature=0.7,
        n=1,
    )
    return response['choices'][0]['message']['content'].strip()

if 'conversation' not in st.session_state:
    st.session_state.conversation = []
    st.session_state.user_input = ''

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
    response = get_openai_response(st.session_state.conversation)

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
    summary = get_openai_response(summary_prompt)

    # Display summary
    st.markdown("### Summary and Key Insights")
    st.write(summary)

    # Reset for new entry
    st.session_state.conversation = []
    st.session_state.user_input = ''

# Update user input in session state
st.session_state.user_input = user_input

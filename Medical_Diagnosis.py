import streamlit as st
import base64
import os
from dotenv import load_dotenv
import tempfile
from groq import Groq
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Retrieve API key from environment variables
api_key = os.getenv("GROQ_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("GROQ API Key not found. Please set GROQ_API_KEY in your .env file.")
    st.stop()

# Initialize the Groq client
client = Groq(api_key=api_key)

# Initializing Google API key
genai.configure(api_key=google_api_key)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

# Sample prompt for image analysis
sample_prompt = [
    """
You are a highly skilled expert in medical image analysis, and your task is to examine medical images to identify any health-related issues and generate a detailed response base on below bullets points e.g(1,2,3,-). 
You are working for a renowned hospital and your expertise is crucial in guiding clinical decisions.

**Your responsibilities are:**
1. **Detailed Analysis**: Scrutinize the image carefully, identifying any abnormalities, injuries, or conditions.
2. **Analysis Report**: Provide a detailed report of your findings, including a clear description of the image's health-related issues.
3. **Recommendations**: Based on the findings, suggest any further tests, treatments, or actions required.
4. **Treatments**: If applicable, recommend treatments or medical actions that could help the patient recover.

**Important Guidelines:**
- Only respond if the image pertains to human health issues.
- If the image is unclear or difficult to interpret, state: "Unable to be correctly determined from the provided image."
- Include the following **disclaimer**: "Consult with a doctor before making any decisions based on this analysis."

**Response Format:**
- **Detailed Analysis**: [Provide a thorough, detailed analysis of the image]
- **Analysis Report**: [Offer a well-structured summary of your findings]
- **Recommendations**: [Suggest necessary steps for further evaluation or treatment]
- **Treatments**: [Provide treatment options or actions based on the findings]

Please proceed with this structured format.
"""
]


  # Initialize the Google Generative AI model
model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config=generation_config,
        safety_settings=safety_settings
    )


# Streamlit UI
st.title("Medical Diagnosis Chatbot using Multi-modal LLM 👨‍⚕️ 🩺 🏥")
st.write("Upload a medical image to receive an AI-powered analysis.")


# File upload section
uploaded_file = st.file_uploader("Upload a Medical Image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        st.session_state['uploaded_file'] = temp_file.name
        st.image(uploaded_file, caption="Uploaded Image")
        

        
ana_button = st.button("Analyze Image")       
# Analyze button

if ana_button:
    image_data = uploaded_file.getvalue()
        
    image_parts = [
            {
                "mime_type" : "image/jpg",
                "data" : image_data
            }
        ]
        
        #     making our prompt ready
    prompt_parts = [
            image_parts[0],
            sample_prompt[0],
        ]
        #generate response
        
    gen_response = model.generate_content(prompt_parts)
    
        
    if gen_response:
            st.title('Detailed analysis based on the uploaded image')
            # st.write(gen_response.text)
            st.session_state['result'] =  gen_response.text
            st.markdown(st.session_state['result'], unsafe_allow_html=False)  
    else:
        st.error("Failed to generate a response. Please try again.")
            
    
    


# Function to simplify the explanation (ELI5)
def explain_like_5(gen_response_text):
    eli5_prompt = "Explain the following information to a 5-year-old:\n" + gen_response_text
    messages = [{"role": "user", "content": eli5_prompt}]

    # Generate simplified explanation
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=2500
    )
    return response.choices[0].message.content



# ELI5 Explanation Section
if 'result' in st.session_state and st.session_state['result']:
    st.write("---")
    st.info("Below you have an option to understand in simpler terms.")
    if st.radio("Explain in Easy Words?", ('No', 'Yes')) == 'Yes':
        simplified_explanation = explain_like_5(st.session_state['result'])
        st.markdown(simplified_explanation, unsafe_allow_html=True)


# Footer
st.write("---")
st.caption("Powered by Groq & Google Gemni LLM | Please consult with a doctor before making any medical decisions.")

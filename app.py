import streamlit as st
import requests
st.info("Upload a PDF and ask questions. The system will answer using only document content.")

API_URL = "https://ask-anything-api.onrender.com"

st.set_page_config(page_title="AI Document Chatbot", layout="centered")

st.title("📄 AI Document Chatbot")
st.markdown("Upload a PDF and ask questions based on its content.")

# Upload section
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Uploading document..."):
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(f"{API_URL}/upload", files=files)

        if response.status_code == 200:
            st.success("Document uploaded successfully!")
        else:
            st.error("Upload failed")

# Question section
st.divider()
question = st.text_input("Ask a question from your document")

if st.button("Get Answer"):
    if question:
        with st.spinner("Generating answer..."):
            res = requests.get(f"{API_URL}/ask-doc", params={"q": question})
            data = res.json()

            if "answer" in data:
                st.subheader("Answer")
                st.write(data["answer"])

                if "sources" in data:
                    st.subheader("Sources")
                    for s in data["sources"]:
                        st.markdown(f"**Page {s['page']}**")
                        st.caption(s["preview"])
            else:
                st.error(data.get("detail", "Something went wrong"))
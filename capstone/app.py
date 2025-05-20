import streamlit as st
import cv2
import numpy as np
import os
from skimage.metrics import structural_similarity as ssim
from PIL import Image
from datetime import datetime
import io
from fpdf import FPDF
from datetime import datetime
import io
import base64


# Function to calculate SSIM
def compare_images(image1, image2):
    image1 = cv2.resize(image1, (256, 256))
    image2 = cv2.resize(image2, (256, 256))
    grayA = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    score, _ = ssim(grayA, grayB, full=True)
    return score

# Load reference images
@st.cache_data
def load_reference_images():
    references = {}
    ref_dir = "reference_images"
    for file in os.listdir(ref_dir):
        if file.endswith((".jpg", ".png", ".jpeg")):
            img = cv2.imread(os.path.join(ref_dir, file))
            label = os.path.splitext(file)[0]
            references[label] = img
    return references

# Sidebar with navigation
menu = st.sidebar.radio("Menu", ["Home", "About Us", "Prediction Process"])

# Load and display logo in the sidebar
st.sidebar.image("Logo/Logo3.png", width=150)  # Replace "your_logo.png" with the actual logo filename

# Global Styling using CSS
st.markdown("""
    <style>
    /* Apply a darker green background across all sections */
    .main, .block-container, .css-18e3th9, .css-1d391kg, .css-1cypcdb {
        background-color: #013220 !important;  /* Darker green */
        color: white;
    }

    html, body, [class*="css"]  {
        font-family: 'Times New Roman', serif;
        font-size: 16px;
        color: white;
    }

    /* Sidebar styling - even darker green for depth */
    .css-1d391kg {
        background-color: #002610 !important;
    }

    /* Center circular image in About Us */
    .circle-image {
        border-radius: 50%;
        width: 150px;
        height: 150px;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
""", unsafe_allow_html=True)


# Home Section
if menu == "Home":
    st.title("Welcome to Cacao Leaf Disease Prediction")
    st.write("""
        This app uses image comparison techniques to predict the health of cacao leaves.
        Upload an image of a cacao leaf, and it will compare it with known disease samples to determine the condition of the leaf.
    """)
    st.write("Use the menu in the sidebar to navigate through the app.")

# About Us Section
elif menu == "About Us":
    # About Us content with background
    st.markdown('<div class="about-us-container">', unsafe_allow_html=True)
    st.title("About Us")
    st.write("""
        <p class="about-us-text">
        We are a team dedicated to improving cacao farming by providing farmers with tools for early disease detection.
        Our mission is to help cacao farmers protect their crops and improve yield quality.
        The disease prediction tool leverages advanced image comparison techniques to analyze leaf images.
        </p>
    """, unsafe_allow_html=True)

    # Circle image with description and centering
    st.write("### Meet Our Team Member:")
    
    # Add circular image (replace with your image)
    st.markdown('<div class="circle-image">', unsafe_allow_html=True)
    st.image("member/frans.jpg", use_column_width=False, width=350, caption="Francis John B. Cantiga", output_format="JPEG")
    st.markdown('</div>', unsafe_allow_html=True)

    # Add a description
    st.write("""
        <p class="about-us-text">
        Francis John B. Cantiga is one of the team members behind this project. He specializes in machine learning and computer vision, bringing cutting-edge technology to the agricultural sector.
        </p>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


    # Add circular image (replace with your image)
    st.markdown('<div class="circle-image">', unsafe_allow_html=True)
    st.image("member/frans.jpg", use_column_width=False, width=350, caption="Joy Monter", output_format="JPEG")
    st.markdown('</div>', unsafe_allow_html=True)

    # Add a description
    st.write("""
        <p class="about-us-text">
        Joy Monter is one of the team members behind this project. He specializes in machine learning and computer vision, bringing cutting-edge technology to the agricultural sector.
        </p>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    

# Prediction Process Section

elif menu == "Prediction Process":
    st.title("Prediction Process")
    st.write("""
        Upload an image of a cacao leaf and the app will compare it to known disease samples using CNN (CONVOLUTIONAL NEURAL NETWORK ).
    """)

    st.image("Logo/logo1.png")

    uploaded_file = st.file_uploader("Choose a cacao leaf image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Convert uploaded image
        uploaded_image = Image.open(uploaded_file)
        st.image(uploaded_image, caption="Uploaded Leaf Image", use_column_width=True)
        uploaded_cv2 = cv2.cvtColor(np.array(uploaded_image), cv2.COLOR_RGB2BGR)

        # Load reference images dynamically
        def load_reference_images():
            ref_dir = "reference_images"
            references = {}
            for file in os.listdir(ref_dir):
                if file.endswith((".jpg", ".jpeg", ".png")):
                    label = os.path.splitext(file)[0]
                    disease_name = "_".join(label.split("_")[:-1]) if "_" in label else label
                    img = cv2.imread(os.path.join(ref_dir, file))
                    if disease_name not in references:
                        references[disease_name] = []
                    references[disease_name].append(img)
            return references

        # SSIM Comparison Function
        def compare_images(img1, img2):
            img1 = cv2.resize(img1, (256, 256))
            img2 = cv2.resize(img2, (256, 256))
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            score, _ = ssim(gray1, gray2, full=True)
            return score

        # Load references and compare
        references = load_reference_images()
        disease_scores = {}

        for disease, images in references.items():
            scores = [compare_images(uploaded_cv2, ref_img) for ref_img in images]
            avg_score = sum(scores) / len(scores)
            disease_scores[disease] = avg_score

        # Sort by best match
        sorted_results = sorted(disease_scores.items(), key=lambda x: x[1], reverse=True)
        top_prediction, top_score = sorted_results[0]

        # Format name nicely
        def format_name(name):
            return name.replace("_", " ").title()

        # Suggestions
        disease_suggestions = {
         "black_pod": "Prune trees regularly, apply copper-based fungicide, and destroy infected pods.",
            "witchesbroom_pod": "Cut and burn infected branches. Use disease-resistant varieties and control humidity.",
            "frosty_pod": "Prevention : Remove and destroy infected pods, manage shade, and apply biological control.",
            "spot_pod": "Use resistant varieties and fungicides. Avoid overhead irrigation.",
            "rusty_pod": "Prune infected branches, plant at recommended spacing, and ensure good drainage.",
             "healthy" : "WOW KA HEALTHY OY! SANAOL!"
        }

        # Display prediction
        st.success(f"🩺 Predicted Condition: **{format_name(top_prediction)}** (Avg CNN: {top_score:.2f})")
        
        # Show top 3 matches
        st.write("### 🔍 Top 3 Disease Matches:")
        for disease, score in sorted_results[:3]:
            st.write(f"✔️ {format_name(disease)} — CNN Score: **{score:.2f}**")

                

        # Show suggestion if available
        suggestion = disease_suggestions.get(top_prediction, ...)

        
        st.subheader("Suggested Prevention or Cure:")
        st.info(suggestion)
        # Generate downloadable report
        report_text = f"""
        Cacao Leaf Disease Detection Report
        ------------------------------------
        Prediction Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
      
        Similarity Score (CNN): {top_score:.2f}
        
        Suggested Prevention or Cure:
        {suggestion}
        """
       
        # Convert to a downloadable text file
        report_bytes = io.BytesIO()
        report_bytes.write(report_text.encode('utf-8'))
        report_bytes.seek(0)

        st.download_button(
            label="📄 Download Report",
            data=report_bytes,
            file_name=f"{top_prediction}_report.txt",
            mime="text/plain"
        )
        # PDF report generation
        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 12)
                self.cell(0, 10, "Cacao Leaf Disease Detection Report", ln=True, align="C")

            def footer(self):
                self.set_y(-15)
                self.set_font("Arial", "I", 8)
                self.cell(0, 10, f"Page {self.page_no()}", align="C")

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add prediction results
        pdf.cell(0, 10, f"Prediction Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.ln(5)
        pdf.cell(0, 10, f"Predicted Leaf Condition: {top_prediction.replace('_', ' ').title()}", ln=True)
        pdf.cell(0, 10, f"Similarity Score (CNN): {top_score:.2f}", ln=True)
        pdf.ln(5)
        pdf.multi_cell(0, 10, f"Suggested Prevention or Cure:\n{suggestion}")

        # Save uploaded image as a temporary file
        image_path = "temp_uploaded_image.jpg"
        uploaded_image.save(image_path)

        # Insert image in PDF
        pdf.ln(10)
        pdf.cell(0, 10, "Uploaded Leaf Image:", ln=True)
        pdf.image(image_path, x=10, w=pdf.w - 20)  # Adjust width to fit the page

        # Convert PDF to downloadable bytes
        pdf_bytes = pdf.output(dest='S').encode('latin-1')  # get PDF as bytes
        pdf_output = io.BytesIO(pdf_bytes)

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_output,
            file_name=f"{top_prediction}_report.pdf",
            mime="application/pdf"
        )




   
      



               

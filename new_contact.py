import streamlit as st
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create connection to Neon PostgreSQL"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT'),
        sslmode='require'
    )

def insert_contact(name, phone, email, address):
    """Insert new contact and return the created record"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Insert and return the new contact
                cur.execute("""
                    INSERT INTO CONTACTS (NAME, PHONE, EMAIL, ADDRESS)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, name, phone, email, address
                """, (name, phone, email, address))
                
                new_contact = cur.fetchone()
                conn.commit()
                return new_contact
                
    except psycopg2.Error as e:
        st.error(f"Database error: {str(e)}")
        return None

# Streamlit Page Configuration
st.set_page_config(page_title="Contact Manager", layout="wide")

# Contact Form Section
st.header("📝 Add New Contact")

with st.form("contact_form", clear_on_submit=True):
    cols = st.columns(2)
    with cols[0]:
        name = st.text_input("Full Name*", help="Required field")
        phone = st.text_input("Phone Number*", 
                            max_chars=10, 
                            help="10 digits without country code")
    with cols[1]:
        email = st.text_input("Email Address*")
        address = st.text_input("Physical Address")
    
    submitted = st.form_submit_button("💾 Save Contact")
    
    if submitted:
        # Validation
        errors = []
        if not name: errors.append("Name is required")
        if not phone: errors.append("Phone is required")
        if not email: errors.append("Email is required")
        
        if phone and (not phone.isdigit() or len(phone) != 10):
            errors.append("Phone must be 10 digits")
            
        if email and '@' not in email:
            errors.append("Invalid email format")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            # Convert phone to integer
            try:
                phone_int = int(phone)
            except ValueError:
                st.error("Phone number must contain only digits")
                st.stop()
            
            # Insert into Neon
            result = insert_contact(
                name.strip(),
                phone_int,
                email.strip(),
                address.strip() if address else None
            )
            
            if result:
                st.success("Contact created successfully! 🎉")
                st.balloons()
                
                # Display the created contact
                st.subheader("New Contact Details", divider="green")
                
                # Format phone number
                phone_str = str(result[2]).zfill(10)
                formatted_phone = f"({phone_str[:3]}) {phone_str[3:6]}-{phone_str[6:]}"
                
                # Create DataFrame for display
                contact_df = pd.DataFrame([{
                    "ID": result[0],
                    "Name": result[1],
                    "Phone": formatted_phone,
                    "Email": result[3],
                    "Address": result[4] if result[4] else "N/A"
                }])
                
                # Show styled dataframe
                st.dataframe(
                    contact_df,
                    use_container_width=True,
                    column_config={
                        "ID": st.column_config.NumberColumn("ID"),
                        "Phone": "Phone Number",
                        "Email": "Email Address"
                    },
                    hide_index=True
                )
                
                # Show raw JSON response
                with st.expander("View Raw Database Response"):
                    st.json({
                        "id": result[0],
                        "name": result[1],
                        "phone": result[2],
                        "email": result[3],
                        "address": result[4]
                    })

# To run: streamlit run your_app.py
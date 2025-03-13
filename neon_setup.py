import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Neon connection with SSL
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=os.getenv('DB_PORT'),
    sslmode='require'
)
cursor = conn.cursor()

# Create Contacts table (Neon-compatible)
cursor.execute("""
CREATE TABLE IF NOT EXISTS CONTACTS (
    ID SERIAL PRIMARY KEY,
    NAME VARCHAR(100) NOT NULL,
    PHONE BIGINT UNIQUE NOT NULL CHECK(PHONE BETWEEN 1000000000 AND 9999999999),
    EMAIL VARCHAR(100) UNIQUE NOT NULL,
    ADDRESS TEXT
);
""")


# Insert contacts (using ON CONFLICT DO NOTHING)
contacts_data = [
    ('Shivansh Shukla', 9876543210, 'abcd@gmail.com', '123, Lorem Ipsum Street, New York, NY 10001'),
    ('Shivansh Shukla', 9999701072, 'dashingshiv10@gmail.com', 'Delhi'),
    ('Sahil Repuriya', 9999701034, 'srepuriya24@gmail.com', 'Delhi'),
    ('Sher Khan', 9999701071, 's20235428@gmail.com', 'Delhi 110088'),
    ('John Doe', 5551234123, 'john@example.com', '123 Main St'),
    ('ishani', 1234567890, 'john.new@example.com', '456 New St'),
    ('Vaibhav', 9999807097, 'vaibhav@gmail.com', 'jaipur'),
    ('mohit', 9920128977, 'mohit@gmail.com', 'mumbai')
]

insert_contact = """
INSERT INTO CONTACTS (NAME, PHONE, EMAIL, ADDRESS) 
VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING
"""
cursor.executemany(insert_contact, contacts_data)
# Note: If you need the generated IDs for later use,
# you must query them after insertion or use RETURNING in the query.

# Create Tasks table
cursor.execute("""
CREATE TABLE IF NOT EXISTS TASKS (
    ID SERIAL PRIMARY KEY,
    TITLE VARCHAR(255) NOT NULL,
    DESCRIPTION TEXT,
    CATEGORY VARCHAR(50),
    PRIORITY TEXT CHECK(PRIORITY IN ('Low', 'Medium', 'High')),
    EXPECTED_OUTCOME TEXT,
    DEADLINE TIMESTAMP NOT NULL,
    ASSIGNED_TO INT NOT NULL REFERENCES CONTACTS(ID),
    DEPENDENCIES TEXT,
    REQUIRED_RESOURCES TEXT,
    ESTIMATED_TIME TEXT NOT NULL,
    INSTRUCTIONS TEXT,
    REVIEW_PROCESS TEXT,
    PERFORMANCE_METRICS TEXT,
    SUPPORT_CONTACT INT REFERENCES CONTACTS(ID),
    NOTES TEXT,
    STATUS TEXT CHECK(STATUS IN ('Not Started', 'In Progress', 'On Hold', 'Completed', 'Reviewed & Approved')) NOT NULL DEFAULT 'Not Started',
    STARTED_AT TIMESTAMP,
    COMPLETED_AT TIMESTAMP
);
""")

# Example: Query to retrieve a contact's ID using one of their unique fields (e.g., PHONE)
cursor.execute("SELECT ID, PHONE FROM CONTACTS;")
contacts = cursor.fetchall()
# Create a dictionary mapping phone to contact ID for later use
contact_ids = {row[1]: row[0] for row in contacts}

# Insert tasks data
tasks_data = [
    (
        'Project Planning', 
        'Plan the initial phase of the project', 
        'Project Management', 
        'High', 
        'Completed project plan document', 
        '2025-03-12 23:59', 
        contact_ids.get(9999701072),  # Adjust this lookup as needed
        'None', 
        'Project management software', 
        '1 week', 
        '1. Define scope\n2. Identify stakeholders', 
        'Review by project manager', 
        '2025-02-10', 
        contact_ids.get(9999701072),  # Support contact
        'Critical initial task', 
        'In Progress',
        '2025-02-25 10:00',  # STARTED_AT
        None  # COMPLETED_AT
    ),
    (
        'Database Setup', 
        'Set up the database schema and tables', 
        'Technical', 
        'Medium', 
        'Functional database system', 
        '2025-03-11 18:00', 
        contact_ids.get(9999701034),  # Sahil Repuriya
        'Project Planning', 
        'SQL tools, Server access', 
        '3 days', 
        '1. Create schema\n2. Define tables', 
        'Review by lead developer', 
        '2025-02-11', 
        contact_ids.get(9999701034),  # Support contact
        'Ensure backup strategy', 
        'Not Started',
        None,
        None
    ),
    (
        'UI Design', 
        'Design the user interface', 
        'Creative', 
        'Medium', 
        'Approved UI mockups', 
        '2025-03-11 12:00', 
        contact_ids.get(9999701071),  # Sher Khan
        'Database Setup', 
        'Design software', 
        '2 weeks', 
        '1. Wireframe\n2. Prototype', 
        'Client review', 
        'User feedback score', 
        contact_ids.get(9999701071),  # Support contact
        'Mobile-first approach', 
        'In Progress',
        '2025-03-01 14:30',
        None
    ),
    (
        'Testing', 
        'Perform unit and integration testing', 
        'QA', 
        'High', 
        'Test report', 
        '2025-03-11 17:00', 
        contact_ids.get(9876543210),  # Adjust this lookup as needed
        'UI Design', 
        'Testing frameworks', 
        '5 days', 
        '1. Write test cases\n2. Execute tests', 
        'QA manager review', 
        'Bug count', 
        contact_ids.get(9876543210),  # Support contact
        'Automate where possible', 
        'Not Started',
        None,
        None
    )
]


insert_task = """
INSERT INTO TASKS (
    TITLE, DESCRIPTION, CATEGORY, PRIORITY, EXPECTED_OUTCOME, DEADLINE,
    ASSIGNED_TO, DEPENDENCIES, REQUIRED_RESOURCES, ESTIMATED_TIME,
    INSTRUCTIONS, REVIEW_PROCESS, PERFORMANCE_METRICS, SUPPORT_CONTACT,
    NOTES, STATUS, STARTED_AT, COMPLETED_AT
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
cursor.executemany(insert_task, tasks_data)

conn.commit()
conn.close()

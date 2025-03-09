import sqlite3
from datetime import datetime

# Connect to (or create) the database and enable foreign keys
conn = sqlite3.connect('test.db')
conn.execute("PRAGMA foreign_keys = 1")
cursor = conn.cursor()

# Create Contacts table
contacts_table = """
CREATE TABLE IF NOT EXISTS CONTACTS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME VARCHAR(100) NOT NULL,
    PHONE INTEGER UNIQUE NOT NULL CHECK(LENGTH(PHONE) = 10),
    EMAIL VARCHAR(100) UNIQUE NOT NULL,
    ADDRESS TEXT
);
"""
cursor.execute(contacts_table)

# Insert dummy contacts data
contacts_data = [
    ('Shivansh Shukla', 9876543210, 'dashingshiv10@gmail.com', '123, Lorem Ipsum Street, New York, NY 10001'),
    ('Mahi Fan', 9999701072, 'shivanshshuklatech@gmail.com', 'Delhi'),
    ('Sahil Repuriya', 9999701034, 'srepuriya24@gmail.com', 'Delhi'),
    ('Sher Khan', 9999701071, 's20235428@gmail.com', 'Delhi 110088'),
    ('John Doe', 5551234123, 'john@example.com', '123 Main St'),
    ('ishani', 1234567890, 'john.new@example.com', '456 New St'),
    ('Vaibhav', 9999807097, 'vaibhav@gmail.com', 'jaipur'),
    ('mohit', 9920128977, 'mohit@gmail.com', 'mumbai')
]
cursor.executemany("INSERT INTO CONTACTS (NAME, PHONE, EMAIL, ADDRESS) VALUES (?, ?, ?, ?)", contacts_data)

# Retrieve contact IDs based on phone numbers
cursor.execute("SELECT PHONE, ID FROM CONTACTS")
contact_ids = {row[0]: row[1] for row in cursor.fetchall()}

# Create updated Tasks table with new columns
tasks_table = """
CREATE TABLE IF NOT EXISTS TASKS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    TITLE VARCHAR(255) NOT NULL,
    DESCRIPTION TEXT,
    CATEGORY VARCHAR(50),
    PRIORITY TEXT CHECK(PRIORITY IN ('Low', 'Medium', 'High')),
    EXPECTED_OUTCOME TEXT,
    DEADLINE DATETIME NOT NULL,
    ASSIGNED_TO INTEGER NOT NULL,
    DEPENDENCIES TEXT,
    REQUIRED_RESOURCES TEXT,
    ESTIMATED_TIME TEXT NOT NULL,
    INSTRUCTIONS TEXT,
    REVIEW_PROCESS TEXT,
    PERFORMANCE_METRICS TEXT,
    SUPPORT_CONTACT INTEGER,
    NOTES TEXT,
    STATUS TEXT CHECK(STATUS IN ('Not Started', 'In Progress', 'On Hold', 'Completed', 'Reviewed & Approved')) NOT NULL DEFAULT 'Not Started',
    STARTED_AT DATETIME,
    COMPLETED_AT DATETIME,
    FOREIGN KEY (ASSIGNED_TO) REFERENCES CONTACTS(ID),
    FOREIGN KEY (SUPPORT_CONTACT) REFERENCES CONTACTS(ID)
);
"""
cursor.execute(tasks_table)

# Prepare and insert tasks data for 4 dummy task entries
tasks_data = [
    (
        'Project Planning', 
        'Plan the initial phase of the project', 
        'Project Management', 
        'High', 
        'Completed project plan document', 
        '2025-03-11 23:59', 
        contact_ids[9999701072],  # Mahi Fan
        'None', 
        'Project management software', 
        '1 week', 
        '1. Define scope\n2. Identify stakeholders', 
        'Review by project manager', 
        '2025-02-10', 
        contact_ids[9999701072],  # Mahi Fan as support too
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
        contact_ids[9999701034],  # Sahil Repuriya
        'Project Planning', 
        'SQL tools, Server access', 
        '3 days', 
        '1. Create schema\n2. Define tables', 
        'Review by lead developer', 
        '2025-02-11', 
        contact_ids[9999701034],  # Sahil Repuriya as support too
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
        contact_ids[9999701071],  # Sher khan
        'Database Setup', 
        'Design software', 
        '2 weeks', 
        '1. Wireframe\n2. Prototype', 
        'Client review', 
        'User feedback score', 
        contact_ids[9999701071],  # Sher khan
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
        contact_ids[9876543210],  # mohit
        'UI Design', 
        'Testing frameworks', 
        '5 days', 
        '1. Write test cases\n2. Execute tests', 
        'QA manager review', 
        'Bug count', 
        contact_ids[9876543210],  # mohit as support too
        'Automate where possible', 
        'Not Started',
        None,
        None
    )
]

insert_query = """
INSERT INTO TASKS (
    TITLE, DESCRIPTION, CATEGORY, PRIORITY, EXPECTED_OUTCOME, DEADLINE,
    ASSIGNED_TO, DEPENDENCIES, REQUIRED_RESOURCES, ESTIMATED_TIME,
    INSTRUCTIONS, REVIEW_PROCESS, PERFORMANCE_METRICS, SUPPORT_CONTACT,
    NOTES, STATUS, STARTED_AT, COMPLETED_AT
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

cursor.executemany(insert_query, tasks_data)
conn.commit()
conn.close()

print("Dummy data inserted successfully!")

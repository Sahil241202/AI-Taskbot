# Deadline Notifier

This project is an automated task deadline notification system that retrieves upcoming deadlines from an SQLite database and sends personalized email reminders using the SendGrid API. It also integrates with the Gemini AI model to generate motivational email content.

## Prerequisites

Ensure you have the following installed:
- Python 3.x
- SQLite3
- pip (Python package manager)

## Installation & Setup

1. **Clone the repository**
   ```sh
   git clone <repository_url>
   cd <repository_name>
   ```

2. **Create a virtual environment (optional but recommended)**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Create a `.env` file in the project root and add the following:
     ```sh
     SENDGRID_API_KEY=your_sendgrid_api_key
     GEMINI_API_KEY=your_gemini_api_key
     ```

5. **Run the script**
   ```sh
   python main.py
   ```

The script will check for tasks due in 2 days and send email reminders automatically.

## Scheduler
- The script runs a scheduler to check and send emails at 10:00 AM daily.
- Modify the time in `scheduler.add_job(check_and_notify, 'cron', hour=10, minute=0)` if needed.

## Contributing
Feel free to submit pull requests for improvements or bug fixes.


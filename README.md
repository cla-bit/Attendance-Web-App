```markdown
# Django Project Setup Guide

## Instructions

### 1. Download the Project from GitHub Repository
Clone the repository to your local machine using the following command:
```bash
git clone <repository_url>
```

### 2. Open the Project in Your IDE
Navigate to the project directory and open it in your preferred Integrated Development Environment (IDE).

### 3. Create a Virtual Environment
Create a virtual environment to manage your project's dependencies:
```bash
python -m venv env
```

### 4. Change Directory into the Project
Navigate into the project directory:
```bash
cd <project_directory>
```

### 5. Install Requirements
Install the required packages using `pip`:
```bash
pip install -r requirements.txt
```

### 6. Run the `makemigrations` Command and `migrate` Command
Create the necessary database migrations and apply them:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a Super User
Create a superuser account to access the Django admin interface:
```bash
python manage.py createsuperuser
```

### 8. Run the Server
Start the development server:
```bash
python manage.py runserver
```

### 9. Create Dummy Data in the Admin Page
Access the admin interface to create dummy data:
- Open your web browser and go to `http://127.0.0.1:8000/admin`
- Log in using the superuser credentials you created
- Add dummy data for testing purposes

### 10. Test Your Dummy Data in Both Student and Lecturer Dashboards
Verify that the dummy data appears correctly in both the student and lecturer dashboards.

## Additional Information
- Ensure your virtual environment is activated before running any commands.
- If you encounter any issues, check the project's documentation or seek help from the community.

Feel free to reach out if you have any questions or need further assistance!
```

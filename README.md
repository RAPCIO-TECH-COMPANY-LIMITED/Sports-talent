EA Football Talent

EA Football Talent is a web platform designed to bridge the gap between undiscovered football talent in East Africa (Uganda, Kenya, Tanzania) and professional clubs or scouts. The platform provides players with a stage to showcase their skills by uploading videos, and offers clubs a powerful tool to discover, analyze, and connect with the next generation of stars.

About The Project

In East Africa, countless talented footballers lack the visibility needed to advance their careers. Traditional scouting is limited in reach and often misses hidden gems. This project solves that pain point by creating a centralized, data-driven platform where talent can be seen and objectively evaluated.

Our key innovation is the integration of AI to automatically analyze video footage, providing scouts with objective metrics and saving them hundreds of hours of manual review.

Key Features

    Dual User Roles: Separate registration and dashboard experiences for Players and Clubs/Scouts.

    Player Profiles: Players can create detailed profiles with their bio, position, country, and age.

    Video Uploads: A user-friendly interface for players to upload their highlight reels and skill videos.

    Talent Discovery: A searchable gallery for clubs to browse all registered players.

    AI-Powered Video Analysis (Phase 1):

        Automatic video tagging for key events (e.g., "Shot Change", "Football").

        Clickable timestamps on videos to jump directly to key moments.

        Powered by Google Cloud Video Intelligence API and processed in the background with Celery.

    Secure Authentication: Robust login, logout, and registration system.

    Role-Based Dashboards: After logging in, users are automatically redirected to their specific dashboard.

Built With

    Backend: Python, Django

    Frontend: HTML, CSS, JavaScript

    Database: SQLite (for development)

    Background Tasks: Celery

    Message Broker: Redis

    External APIs: Google Cloud Video Intelligence API

Getting Started

Follow these instructions to get a local copy of the project up and running for development and testing.

Prerequisites

You must have the following installed on your system:

    Python 3.8+

    pip and venv

    Redis (redis-server)

    A Google Cloud Platform account with the Video Intelligence API enabled and a JSON service account key.

Installation & Setup

    Clone the repository (example):
    Bash

git clone https://github.com/your-username/ea-football-talent.git
cd ea-football-talent

Create and activate a virtual environment:
Bash

# For Linux/macOS/WSL
python3 -m venv venv
source venv/bin/activate

Install Python dependencies:
Bash

pip install -r requirements.txt

Configure Google Cloud Credentials:

    Place your downloaded Google Cloud JSON key file in the project's root directory.

    Open core/tasks.py and update the credentials_path variable to match your JSON key's filename.
    Python

    # core/tasks.py
    credentials_path = os.path.join(os.path.dirname(__file__), '..', 'your-key-file.json')

Run database migrations:
Bash

    python manage.py migrate

Usage

To run the full application, you need to start three separate processes in three different terminals. Make sure you are in the project root and have activated the virtual environment in each terminal.

    Terminal 1: Start Redis
    Bash

redis-server

Terminal 2: Start the Celery Worker
Bash

celery -A talentplatform.celery worker -l info

Terminal 3: Start the Django Development Server
Bash

    python manage.py runserver

The application will be available at http://127.0.0.1:8000/.

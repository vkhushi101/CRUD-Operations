import subprocess
import os
import sys
from dotenv import load_dotenv

# Load env variables from .env file
load_dotenv()

# Retrieve the env variables
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
migrations_dir = "./migrations"

# Check if required env variables are set
if not db_host or not db_user or not db_password or not db_name:
    print("Error: Missing 1+ environment variables.")
    sys.exit(1)


# Base Flyway command to be reused for clean and migration operations
# -X enables verbose logging (optional)
def run_flyway(command):
    print(f"Beginning running flyway {command}")
    flyway_command = [
        "flyway",
        "-X",
        f"-url=jdbc:mysql://{db_host}:3306/{db_name}",
        f"-user={db_user}",
        f"-password={db_password}",
        f"-locations=filesystem:{migrations_dir}",
    ]

    # Specific command appended upon running script (clean and migrate)
    flyway_command.append(command)

    try:
        print(f"Running flyway command {flyway_command}")
        subprocess.run(flyway_command, check=True)
        print(f"Flyway {command} executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during Flyway {command}: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        command = sys.argv[1].lower()

        if command not in ["clean", "migrate"]:
            print(f"Error: '{command}' is not a valid Flyway command.")
        else:
            print(f"Attempting to run Flyway {command}...")
            run_flyway(command)

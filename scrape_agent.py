import os
import csv
import json
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr
from browser_use import Agent
import pandas as pd
import json
import re
import sys

# ──────────────────────────────────────
# Environment & LLM Initialization
# ──────────────────────────────────────

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash-exp',
    api_key=SecretStr(os.getenv('GEMINI_API_KEY'))
)

# ──────────────────────────────────────
# Task for the Agent
# ──────────────────────────────────────
username = sys.argv[1]
password = sys.argv[2]
semester = sys.argv[3]
year_of_study = sys.argv[4]

task = f"""1) Open https://cudportal.cud.ac.ae/student/logout.asp  
2) Login with username **{username}** and password **{password}**, and in the semester selection field, select **{semester}**  
3) Navigate to **Course Offerings**  
4) Click **Show Filter**, select **SEAST** under Divisions  
5) Click **Apply Filter**  
6) For each course on all pages, extract the following fields:  
   - Course  
   - Course Name  
   - Instructor  
   - Room  
   - Days  
   - Credits  
   - Start Time  
   - End Time  
   - Max Enrollment  
   - Total Enrollment  

7) Only include courses that match the selected **year of study = {year_of_study}**.  
To determine the year of a course, use the following rule:  
- The year of the course is the **first digit** in the numeric part of the course code.  
  For example:  
  - `BCS101` → 1st year  
  - `BCS205` → 2nd year  
  - `BCS311` → 3rd year  
  - `BCS421` → 4th year  

So if **year_of_study = {year_of_study}**, only include courses where the course code (e.g., `BCS303`) starts with that year number after the prefix.

8) Return the matching courses in **JSON format**, as a list of objects.
"""

# ──────────────────────────────────────
# Asynchronous Agent Execution
# ──────────────────────────────────────

async def agent_task():
    agent = Agent(task=task, llm=llm)
    history = await agent.run()

    content = history.extracted_content()

    # Try decoding JSON if it's a string
    if isinstance(content, str):
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            print("❌ JSON decode error:", e)
            return
    else:
        data = content

    # Check for empty data
    if not data:
        print("⚠️ No data received or data is empty.")
        return

    # Debug output
    print("Data object type:", type(data))
    print("Number of elements:", len(data))
    print("Type of first element:", type(data[0]))
    print("First element:", data[0])

    # Save to CSV
    csv_file = "courses.csv"
    try:
        if isinstance(data[0], dict):
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            print(f"✅ Saved as table to: {csv_file}")

        elif isinstance(data[0], str):
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in data:
                    writer.writerow([row])
            print(f"✅ Saved as list of strings to: {csv_file}")

        elif isinstance(data[0], list):
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(data)
            print(f"✅ Saved as list table to: {csv_file}")

        else:
            print("❌ Unknown data format. Cannot save.")
            print("Example element:", data[0])

    except Exception as e:
        print("❌ Error saving CSV:", e)

    # Load CSV and extract embedded JSON (if any)
    input_file = "courses.csv"
    df = pd.read_csv(input_file)

    # Extract rows that contain embedded JSON strings
    json_strings = df[df.iloc[:, 0].str.contains(r"\[\s*{", na=False)].iloc[:, 0].tolist()

    # Parse JSON from the strings
    course_data = []
    for text in json_strings:
        match = re.search(r'\[\s*{.*}\s*\]', text, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                course_data.extend(parsed)
            except json.JSONDecodeError:
                continue

    # Convert to DataFrame
    courses_df = pd.DataFrame(course_data)

    # Filter relevant columns
    columns_of_interest = [
        "Course", "Course Name", "Instructor", "Room", "Days", "Credits",
        "Start Time", "End Time", "Max Enrollment", "Total Enrollment"
    ]
    filtered_df = courses_df[columns_of_interest]

    # Save to final CSV
    output_file = "courses.csv"
    filtered_df.to_csv(output_file, index=False)

    print(f"✅ Final course file saved as: {output_file}")


# ──────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────

if __name__ == "__main__":
    asyncio.run(agent_task())

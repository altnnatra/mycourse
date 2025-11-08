
## Offerings Scraper – CUD

### Overview

**Offerings Scraper** is a Streamlit-based web application that automates the collection and analysis of course data from the **Canadian University Dubai (CUD)** student portal.
It provides an intuitive interface to log in, scrape course offerings, store them as a CSV file, and interact with the data using either a **local LLM (Ollama)** or **Anthropic Claude API** for natural language queries.

---

### Features

* **Automated Login & Scraping:**
  Runs a Python browser agent to collect course information from the CUD portal using student credentials.

* **Data Preview:**
  Displays scraped course data in an interactive table with filtering and sorting.

* **LLM-Powered Analysis:**
  Users can ask natural language questions about the courses — the app interprets the CSV and responds using:

  * **Claude (Anthropic API)**
  * **Ollama (local LLM such as Mistral)**

* **Smart Inference:**
  Automatically deduces the **year of study** from the course codes (e.g., `BCS101 → 1st year`, `BCS311 → 3rd year`).

---

### Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **LLM Integration:** Anthropic API / Ollama
* **Data Storage:** CSV (via Pandas)
* **Environment Management:** `python-dotenv`

---

### How It Works

1. Click **“Scrape courses from portal”** in the web app.
2. Enter your CUD credentials, semester, and year of study.
3. The scraper (`scrape_agent.py`) collects data and saves it to `courses.csv`.
4. The app displays the data, allowing you to query it using natural language.

---

### Run Locally

```bash
# Clone the repo
git clone https://github.com/altnnatra/mycourse.git
cd mycourse

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Anthropic API key
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env

# Run the app
streamlit run app.py
```

---

### Example Query

> *“Show me all courses taught by Dr. Said Elnaffar.”*
> *Claude / Mistral replies with a filtered list based on the CSV data.*


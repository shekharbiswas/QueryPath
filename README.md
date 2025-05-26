# 🧭 QueryPath: SQL _growth companion_

**QueryPath** is a focused, reflective SQL learning app.
Designed for adult learners, it combines SQL micro-challenges with habit tracking, self-reflection, and daily progression — helping users *not just learn*, but *grow with purpose*.
Its a MVP prototype.

<br>


<img width="1024" alt="image" src="https://github.com/user-attachments/assets/2c720a43-40d0-41ba-9ece-3b15cd14b9e0" />


<br>
<br>


📺 [**Watch the Demo**  ](https://www.youtube.com/watch?v=2NbHvPD_n-Y)


<br>


## 🌟 Why QueryPath?

Most SQL tutorials throw information at learners.  
**QueryPath takes a different route** — one rooted in behavior design, emotional momentum, and real-world data scenarios.

- 🔁 Short, daily SQL tasks that adapt to your pace
- 📈 Visual confidence tracker and habit streak
- 💬 Reflective questions that deepen your understanding
- 🧠 Spaced repetition of past struggles
- 🧩 Business-inspired context for every challenge

<br>

## 🧑‍🎓 Who It's For

QueryPath is for **self-motivated adults**, career switchers, or upskillers who:

- Learn best through doing
- Struggle to stay consistent with online courses
- Want clarity, calm UI, and minimal distractions
- Value progress over perfection

<br>

## 🗓️ What the 7 Days Look Like

| Day | Theme                      | SQL Focus              | Reflective Prompt                          |
|-----|----------------------------|-------------------------|--------------------------------------------|
| 1   | Getting Your Bearings      | `SELECT`, `FROM`, `WHERE` | "What felt unexpectedly easy today?"       |
| 2   | Filtering Reality          | `AND`, `OR`, comparisons | "How would this help your current job?"    |
| 3   | Ordering Chaos             | `ORDER BY`, `LIMIT`     | "Did any result surprise you?"             |
| 4   | Aggregating Insights       | `GROUP BY`, `COUNT()`   | "Where do you see this used in real life?" |
| 5   | Joining Worlds             | `INNER JOIN`            | "How confident are you with joins?"        |
| 6   | Asking Bigger Questions    | `HAVING`, nested queries| "What’s your mental model for subqueries?" |
| 7   | Project & Reflection       | All skills combined     | "What did you learn about *how* you learn?"|

<br>

## 🛠️ How It Works

- Built with **Streamlit**
- Backend uses **SQLite** to validate query correctness
- Each day pulls a `challenge.json` with:
  - Scenario
  - Target query
  - Expected results
  - Feedback template

<br>

## 🚀 Getting Started

### 1. Clone the Repo
```bash
git clone https://github.com/yourname/querypath.git
cd querypath
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run app.py
```

## 🎨 Design Philosophy

> "This isn’t gamified. It’s grounded."

**QueryPath** uses behavioral design to make SQL practice feel like **meditation — not pressure**.  
From muted tones and soft UI interactions to personal journaling, the app is designed for **consistency, not comparison**.

- Minimal UI, no dashboards or distractions  
- Light/dark themes that support focus  
- Built-in pauses to reflect and write  
- End-of-week growth report  



## 📁 Project structure

```
querypath_app/
├── challenges/
│   ├── day1.json
│   └── day2.json # (and so on)
├── data/
│   └── challenges.db # Your SQLite database
├── core/
│   ├── __init__.py
│   ├── data_loader.py     # Loads challenge JSON
│   ├── db_connector.py    # Handles DB connection
│   ├── query_validator.py # Normalizes and compares DFs
│   └── session_state_manager.py # Manages session state initialization and access
├── ui/
│   ├── __init__.py
│   ├── sidebar.py
│   ├── challenge_display.py
│   ├── query_input.py
│   ├── navigation.py
│   └── feedback_display.py
├── app.py                 # Main Streamlit app script
└── requirements.txt

```



## LLM Integration & System

This document outlines the core integration points for adding a self-hosted LLM for dynamic SQL hints within the QueryPath Streamlit application, along with considerations for a more robust system design if scaling is required.

### I. Core LLM Integration in Streamlit (Simplified)

These are the key steps for integrating a locally-hosted Hugging Face LLM directly within the Streamlit application:

#### 1. LLM Model Initialization & Resource Caching
*   **Goal:** Load the LLM (e.g., from Hugging Face using `transformers` or an Ollama client) and its tokenizer efficiently.
*   **Mechanism:** Use Streamlit's `@st.cache_resource` decorator. This ensures the large model is loaded into memory only once per Streamlit app session, preventing reloads on every user interaction.
*   **Location:** Typically in a helper module like `core/local_llm_helper.py`.

#### 2. User-Triggered Hint Request
*   **Goal:** Allow users to request an AI-generated hint when their SQL query is incorrect.
*   **Mechanism:** An `st.button` (e.g., "🤖 Get AI Hint") in the UI, likely within the feedback display section (`ui/feedback_display.py`). This button becomes active only when a query attempt is marked incorrect.

#### 3. Dynamic Prompt Construction for LLM
*   **Goal:** Provide the LLM with sufficient context to generate a relevant hint.
*   **Mechanism:** A Python function that assembles a prompt string containing:
    *   The user's incorrect SQL query.
    *   The original challenge prompt/question.
    *   Relevant table schema(s) for the current challenge.
    *   Any SQL error message returned by the database.
    *   Clear instructions to the LLM on its role (tutor, provide hints, don't give the full answer).
*   **Note:** Prompt formatting is crucial and model-specific.

#### 4. LLM Inference & Hint Caching
*   **Goal:** Execute the LLM with the constructed prompt and cache the resulting hint to reduce redundant computations for identical incorrect queries.
*   **Mechanism:**
    *   The inference call (e.g., `model.generate()` or an API call to a local Ollama instance).
    *   Streamlit's `@st.cache_data` decorator on the hint generation function. This caches the output (the hint) based on the input arguments (user query, challenge details, etc.).
*   **Location:** The hint generation function in `core/local_llm_helper.py`.

#### 5. Displaying the LLM-Generated Hint
*   **Goal:** Present the AI's hint clearly to the user.
*   **Mechanism:** Use `st.info()`, `st.markdown()`, or an `st.expander()` to display the text returned by the LLM.
*   **Location:** Within the feedback display section (`ui/feedback_display.py`), triggered after the AI hint button is pressed.

### II. Advanced System (for Scalability & Robustness)

If the application needs to support more users or if the LLM becomes a performance bottleneck, consider these concepts:

#### 1. Dedicated LLM Inference Service
*   **Concept:** Decouple the LLM by running it as a separate microservice (e.g., using FastAPI, BentoML, NVIDIA Triton) with its own API endpoint. The Streamlit app then acts as a client to this service.
*   **Benefits:** Independent scaling, resource management, and easier updates for the LLM component.

#### 2. Load Balancer
*   **Concept:** If running multiple instances of the LLM inference service for high availability or throughput, a load balancer (e.g., Nginx, HAProxy) distributes incoming hint requests.
*   **Benefits:** Improved performance and fault tolerance.

#### 3. Enhanced Caching Strategies
*   **Concept:** Beyond Streamlit's built-in caching, implement caching at the LLM inference service level or use a distributed cache (e.g., Redis, Memcached) if multiple Streamlit app instances or other services consume the LLM hints.
*   **Benefits:** Reduced load on LLMs, faster responses for common queries across users/sessions.

#### 4. Request Queuing & Asynchronous Processing
*   **Concept:** For potentially long-running LLM inference tasks, use a message queue (e.g., RabbitMQ, Celery) to process hint requests asynchronously. The Streamlit app submits a request and can poll for results or be notified, preventing UI freezes.
*   **Benefits:** Improved UI responsiveness.

#### 5. Resource Management & Monitoring
*   **Concept:** Actively monitor the resource usage (CPU, GPU, Memory) of the LLM service and set up alerts.
*   **Benefits:** Ensures service stability, helps identify performance issues, and aids in capacity planning.

### III. Initial Focus for QueryPath
For the current QueryPath application, the "Core LLM Integration in Streamlit" (Section I) using `@st.cache_resource` for model loading and `@st.cache_data` for hint caching will likely be sufficient, especially when using tools like Ollama that simplify local model serving. The advanced concepts (Section II) become more relevant if the LLM workload grows significantly.




## ✨ Future Plans
- User accounts (via Google or GitHub OAuth)
- Streak reminders via email
- Dark mode & accessibility improvements
- Exportable end-of-week report (PDF)


## 🧠 Beyond SQL: _Cognitive benefits?_

QueryPath is more than a tool for learning SQL syntax — it's a system to **train how you think**, **notice**, and **solve**.  
Every daily challenge is designed to strengthen mental agility while deepening data intuition.

- **🧠 Improve Memory** — Retain SQL patterns and logic through repetition and reflection  
- **⚡ Increase Speed of Thought** — Make faster, sharper decisions when querying messy datasets  
- **🧩 Train Logical Thinking** — Develop structured, step-by-step approaches to complex problems  
- **📊 Improve Quality of Work** — Write cleaner, more accurate SQL in less time  
- **🔄 Embrace Pattern Recognition** — Spot common query structures and recurring data behaviors  
- **🧭 Build Analytical Confidence** — Move from “guesswork” to deliberate analysis with clarity  

> _“SQL isn’t just a tech skill — it’s a thinking discipline.”_

# 🧭 QueryPath: SQL Growth Companion

**QueryPath** is a focused, reflective SQL learning app.
Designed for adult learners, it combines SQL micro-challenges with habit tracking, self-reflection, and daily progression — helping users *not just learn*, but *grow with purpose*.
Its a MVP prototype.

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
streamlit run app/QueryPath.py
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
querypath/
├── app/
│   └── QueryPath.py            # Main Streamlit app
├── challenges/
│   ├── day1.json               # Daily challenge files
│   ├── ...
├── logic/
│   ├── validator.py            # SQL query validation
│   ├── progress_tracker.py     # Habit & score tracking
├── assets/
│   └── screenshots/            # UI previews
├── README.md
├── requirements.txt
└── GDD.md                      # Game/app design document
```


## ✨ Future Plans
- User accounts (via Google or GitHub OAuth)
- Streak reminders via email
- Dark mode & accessibility improvements
- Exportable end-of-week report (PDF)


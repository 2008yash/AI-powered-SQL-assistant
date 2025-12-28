import streamlit as st
import os
import sqlite3
from dotenv import load_dotenv
from openai import OpenAI

# ---------------- ENV ----------------
load_dotenv()

# ---------------- PAGE CONFIG (FIRST) ----------------
st.set_page_config(
    page_title="AI SQL Assistant",
    layout="centered"
)

# ---------------- DATABASE ----------------
DB_NAME = "student.db"


def init_db(db=DB_NAME):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS STUDENT(
        NAME TEXT,
        CLASS TEXT,
        SECTION TEXT,
        MARKS INTEGER
    )
    """)

    cursor.execute("SELECT COUNT(*) FROM STUDENT")
    if cursor.fetchone()[0] == 0:
        data = [
            ('Ashutosh', 'Gen AI', 'A', 90),
            ('Anupam', 'DGen AI', 'B', 100),
            ('Evanjilin', 'Power BI', 'A', 86),
            ('Nidhi', 'Web DevOps', 'A', 50),
            ('Parshvi', 'Power BI', 'A', 35)
        ]
        cursor.executemany(
            "INSERT INTO STUDENT VALUES (?,?,?,?)", data
        )
        conn.commit()

    conn.close()


def execute_sql_query(sql, db=DB_NAME):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    try:
        cursor.execute(sql)

        if sql.strip().lower().startswith("select"):
            rows = cursor.fetchall()
            conn.close()
            return rows

        conn.commit()
        conn.close()
        return "✅ Query executed successfully"

    except Exception as e:
        conn.close()
        raise e


# Initialize DB
init_db()

# ---------------- OPENAI ----------------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OPENAI_API_KEY not found. Check your .env file")
    st.stop()

client = OpenAI(api_key=api_key)


def get_openai_response(question):
    prompt = f"""
You are an expert SQLite SQL developer.

Convert the user's natural language question into a valid SQLite SQL query.

Rules:
- Output ONLY SQL
- No explanation
- No markdown
- SQLite compatible

Existing table:
STUDENT(NAME, CLASS, SECTION, MARKS)

User question:
{question}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text.strip()


# ---------------- UI ----------------
st.title("🧠 AI-Powered SQL Generator")
st.subheader("C.U. Shah Polytechnic – Surendranagar")

question = st.text_input(
    "Ask your database question in plain English:"
)

submit = st.button("Generate & Run SQL")

if submit and question:
    sql_query = get_openai_response(question)

    st.subheader("Generated SQL Query")
    st.code(sql_query, language="sql")

    try:
        results = execute_sql_query(sql_query)

        st.subheader("Query Results")

        if isinstance(results, list):
            if results:
                for row in results:
                    st.write(row)
            else:
                st.info("No records found")
        else:
            st.success(results)

    except Exception as e:
        st.error(str(e))



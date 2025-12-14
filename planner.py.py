import streamlit as st
from collections import Counter
from pyairtable import Api

st.set_page_config(page_title="Macro Planner", page_icon="📌", layout="wide")

# --- Airtable setup using Streamlit secrets ---
API_TOKEN = st.secrets["API_TOKEN"]
BASE_ID = st.secrets["BASE_ID"]
TASKS_TABLE = "Tasks"
JOURNAL_TABLE = "Journal"

api = Api(API_TOKEN)
tasks_table = api.table(BASE_ID, TASKS_TABLE)
journal_table = api.table(BASE_ID, JOURNAL_TABLE)

priority_icons = {"Urgent":"🔴","Important":"🟡","Defer":"⚪","Wish":"💭"}

def load_tasks():
    records = tasks_table.all()
    return [
        {
            "Title": r["fields"].get("Title",""),
            "Category": r["fields"].get("Category","Task"),
            "Horizon": r["fields"].get("Horizon","Short-Term (0–3 months)"),
            "Priority": r["fields"].get("Priority","Important"),
            "Notes": r["fields"].get("Notes","")
        }
        for r in records
    ]

def load_journal():
    records = journal_table.all()
    return [r["fields"].get("Entry","") for r in records]

def save_tasks(tasks):
    for r in tasks_table.all():
        tasks_table.delete(r["id"])
    for t in tasks:
        tasks_table.create(t)

def save_journal(entries):
    for r in journal_table.all():
        journal_table.delete(r["id"])
    for e in entries:
        journal_table.create({"Entry": e})

if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()
if "journal_entries" not in st.session_state:
    st.session_state.journal_entries = load_journal()

st.sidebar.title("📌 Macro Planner")
page = st.sidebar.radio("Navigate", ["Planner", "Journal"])

priority_counts = Counter([t["Priority"] for t in st.session_state.tasks])
st.sidebar.subheader("📊 Priority Counts")
for p in ["Urgent","Important","Defer","Wish"]:
    st.sidebar.write(f"{priority_icons[p]} {p}: {priority_counts.get(p,0)}")

if page == "Planner":
    st.title("Macro Planner Dashboard")
    with st.sidebar.form("add_form", clear_on_submit=True):
        title = st.text_input("Task / Responsibility / Wish")
        category = st.selectbox("Category", ["Task","Responsibility","Wish","Goal"])
        horizon = st.selectbox("Time Horizon", ["Short-Term (0–3 months)","Long-Term (3+ months)"])
        priority = st.selectbox("Priority", ["Urgent","Important","Defer","Wish"])
        notes = st.text_area("Notes (optional)")
        add_button = st.form_submit_button("Add")
    if add_button and title:
        st.session_state.tasks.append({
            "Title": title,
            "Category": category,
            "Horizon": horizon,
            "Priority": priority,
            "Notes": notes
        })
        save_tasks(st.session_state.tasks)
        st.rerun()
    if st.session_state.tasks:
        st.subheader("📋 Task List")
        for i, task in enumerate(st.session_state.tasks):
            unique_id = f"{i}_{task['Title']}_{task['Horizon']}"
            st.markdown(f"{priority_icons[task['Priority']]} **{task['Title']}** "
                        f"({task['Category']}, {task['Horizon']}, {task['Priority']})")
            with st.expander("View / Edit Notes"):
                st.caption(f"📝 {task['Notes']}" if task["Notes"] else "📝 No notes added.")
                new_title = st.text_input("Edit Title", task["Title"], key=f"title_{unique_id}")
                new_category = st.selectbox("Edit Category", ["Task","Responsibility","Wish","Goal"],
                                            index=["Task","Responsibility","Wish","Goal"].index(task["Category"]),
                                            key=f"cat_{unique_id}")
                new_horizon = st.selectbox("Edit Horizon", ["Short-Term (0–3 months)","Long-Term (3+ months)"],
                                           index=["Short-Term (0–3 months)","Long-Term (3+ months)"].index(task["Horizon"]),
                                           key=f"hor_{unique_id}")
                new_priority = st.selectbox("Edit Priority", ["Urgent","Important","Defer","Wish"],
                                            index=["Urgent","Important","Defer","Wish"].index(task["Priority"]),
                                            key=f"pri_{unique_id}")
                new_notes = st.text_area("Edit Notes", task["Notes"], key=f"notes_{unique_id}")
                col_save, col_delete = st.columns(2)
                if col_save.button("Save Changes", key=f"save_{unique_id}"):
                    st.session_state.tasks[i] = {
                        "Title": new_title,
                        "Category": new_category,
                        "Horizon": new_horizon,
                        "Priority": new_priority,
                        "Notes": new_notes
                    }
                    save_tasks(st.session_state.tasks)
                    st.rerun()
                if col_delete.button("Delete", key=f"del_{unique_id}"):
                    st.session_state.tasks.pop(i)
                    save_tasks(st.session_state.tasks)
                    st.rerun()
    else:
        st.info("No items yet. Add something from the sidebar!")

elif page == "Journal":
    st.title("📓 Journal Entries")
    with st.form("journal_form", clear_on_submit=True):
        entry = st.text_area("Write your journal entry here...")
        add_entry = st.form_submit_button("Save Entry")
    if add_entry and entry:
        st.session_state.journal_entries.append(entry)
        save_journal(st.session_state.journal_entries)
        st.rerun()
    if st.session_state.journal_entries:
        st.subheader("🗂️ Saved Entries")
        for i, entry in enumerate(st.session_state.journal_entries):
            with st.expander(f"Entry {i+1}"):
                st.write(entry)
    else:
        st.info("No journal entries yet. Add one above!")
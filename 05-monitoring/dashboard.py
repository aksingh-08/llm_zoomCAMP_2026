import streamlit as st
from dataclasses import asdict
import pandas as pd
from db_query import get_conversations, get_stats
from db_query import get_conversations, get_stats, get_relevance_stats, get_user_feedback_stats

records = get_conversations(limit=100)
df = pd.DataFrame([asdict(r) for r in records])

st.subheader("Cost over time")
st.line_chart(df, x="timestamp", y="cost")

st.subheader("Response time over time")
st.line_chart(df, x="timestamp", y="response_time")

st.subheader("Recent conversations")
records = get_conversations(limit=20)

st.subheader("Judge relevance")
relevance = get_relevance_stats()
st.bar_chart(relevance)

st.subheader("User feedback")
thumbs_up, thumbs_down = get_user_feedback_stats()
col1, col2 = st.columns(2)
col1.metric("Thumbs up", int(thumbs_up or 0))
col2.metric("Thumbs down", int(thumbs_down or 0))

for record in records:
    st.write(f"**{record.prompt[:80]}...**")
    st.write(f"{record.answer[:200]}...")
    st.write(f"Time: {record.response_time:.2f}s | Cost: ${record.cost:.4f}")
    st.divider()
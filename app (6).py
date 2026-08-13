import streamlit as st
import pandas as pd
import tempfile
import os

from transcribe import transcribe_audio
from analyze import analyze_call

from database_supabase import (
    save_call_analysis,
    get_call_history,
    get_dashboard_data
)

st.set_page_config(
    page_title="AI Call Intelligence",
    page_icon="📞",
    layout="wide"
)

st.title("📞 AI Call Intelligence & Smart Retargeting Platform")

menu = st.sidebar.radio(
    "Navigation",
    ["Analyze Call", "Call History", "Dashboard"]
)

# ---------------- ANALYZE CALL ----------------
if menu == "Analyze Call":
    st.header("🎧 Upload & Analyze Call")

    customer_name = st.text_input("Customer Name", value="")
    phone_number = st.text_input("Phone Number", value="")

    uploaded_file = st.file_uploader(
        "Upload Call Audio File",
        type=["mp3", "wav", "m4a", "ogg"]
    )

    if "transcript" not in st.session_state:
        st.session_state["transcript"] = ""

    if "analysis" not in st.session_state:
        st.session_state["analysis"] = ""

    if uploaded_file is not None:
        st.success("Audio uploaded successfully.")

        if st.button("Transcribe Audio"):
            try:
                with st.spinner("Transcribing audio..."):
                    suffix = os.path.splitext(uploaded_file.name)[1]

                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
                        temp_audio.write(uploaded_file.read())
                        temp_audio_path = temp_audio.name

                    transcript = transcribe_audio(temp_audio_path)
                    st.session_state["transcript"] = transcript

                    os.remove(temp_audio_path)

                st.success("Transcription completed.")

            except Exception as e:
                st.error("Error while transcribing audio.")
                st.exception(e)

    transcript = st.text_area(
        "Call Transcript",
        value=st.session_state["transcript"],
        height=250
    )

    if st.button("Analyze & Save"):
        if not transcript:
            st.warning("Please upload audio and transcribe, or enter transcript manually.")
        else:
            try:
                with st.spinner("Analyzing call..."):
                    analysis = analyze_call(transcript)

                st.session_state["analysis"] = analysis

                st.subheader("AI Analysis Result")
                st.write(analysis)

                with st.spinner("Saving to Supabase..."):
                    saved_data = save_call_analysis(
                        customer_name if customer_name else "Unknown",
                        phone_number if phone_number else "Unknown",
                        transcript,
                        analysis
                    )

                if saved_data:
                    st.success("Call analysis saved successfully to Supabase.")
                else:
                    st.warning("Analysis completed, but save response was empty. Check Supabase table/RLS.")

            except Exception as e:
                st.error("Something went wrong while analyzing or saving.")
                st.exception(e)

    if st.session_state["analysis"]:
        txt_output = f"""
AI CALL ANALYSIS REPORT

Customer Name: {customer_name if customer_name else "Unknown"}
Phone Number: {phone_number if phone_number else "Unknown"}

Transcript:
{transcript}

Analysis:
{st.session_state["analysis"]}
"""

        st.download_button(
            label="Download Analysis as TXT",
            data=txt_output,
            file_name="call_analysis_report.txt",
            mime="text/plain"
        )

# ---------------- CALL HISTORY ----------------
elif menu == "Call History":
    st.header("📋 Call History")

    try:
        history = get_call_history()

        if history:
            df = pd.DataFrame(history)
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False)

            st.download_button(
                label="Download Call History CSV",
                data=csv,
                file_name="call_history.csv",
                mime="text/csv"
            )
        else:
            st.info("No call history available yet.")

    except Exception as e:
        st.error("Unable to load call history.")
        st.exception(e)

# ---------------- DASHBOARD ----------------
# ---------------- DASHBOARD ----------------
elif menu == "Dashboard":
    st.header("📊 Interactive AI Call Intelligence Dashboard")

    try:
        data = get_dashboard_data()

        if data:
            df = pd.DataFrame(data)

            if "analysis" in df.columns:
                df["analysis"] = df["analysis"].astype(str)

            def extract_sentiment(text):
                text = str(text).lower()
                if "positive" in text:
                    return "Positive"
                elif "negative" in text:
                    return "Negative"
                elif "neutral" in text:
                    return "Neutral"
                return "Unknown"

            def extract_segment(text):
                text = str(text).lower()
                if "strike now" in text:
                    return "Strike Now"
                elif "nurture" in text:
                    return "Nurture"
                elif "handle objection" in text:
                    return "Handle Objection"
                elif "re-engage" in text or "reengage" in text:
                    return "Re-engage"
                elif "do not contact" in text:
                    return "Do Not Contact"
                return "Unknown"

            def extract_intent(text):
                text = str(text).lower()
                if "home loan" in text:
                    return "Home Loan"
                elif "personal loan" in text:
                    return "Personal Loan"
                elif "credit card" in text:
                    return "Credit Card"
                elif "insurance" in text:
                    return "Insurance"
                elif "interested" in text:
                    return "Interested"
                return "General Inquiry"

            df["sentiment"] = df["analysis"].apply(extract_sentiment)
            df["retargeting_segment"] = df["analysis"].apply(extract_segment)
            df["intent_category"] = df["analysis"].apply(extract_intent)

            st.subheader("📌 Key Metrics")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Total Calls", len(df))
            col2.metric("Positive Calls", len(df[df["sentiment"] == "Positive"]))
            col3.metric("Hot Leads", len(df[df["retargeting_segment"] == "Strike Now"]))
            col4.metric("Objection Cases", len(df[df["retargeting_segment"] == "Handle Objection"]))

            st.divider()

            import plotly.express as px

            colA, colB = st.columns(2)

            with colA:
                segment_count = df["retargeting_segment"].value_counts().reset_index()
                segment_count.columns = ["Retargeting Segment", "Count"]

                fig_segment = px.bar(
                    segment_count,
                    x="Retargeting Segment",
                    y="Count",
                    title="🎯 Retargeting Segment Distribution",
                    text="Count"
                )
                st.plotly_chart(fig_segment, use_container_width=True)

            with colB:
                sentiment_count = df["sentiment"].value_counts().reset_index()
                sentiment_count.columns = ["Sentiment", "Count"]

                fig_sentiment = px.pie(
                    sentiment_count,
                    names="Sentiment",
                    values="Count",
                    title="😊 Sentiment Distribution"
                )
                st.plotly_chart(fig_sentiment, use_container_width=True)

            colC, colD = st.columns(2)

            with colC:
                intent_count = df["intent_category"].value_counts().reset_index()
                intent_count.columns = ["Intent", "Count"]

                fig_intent = px.bar(
                    intent_count,
                    x="Intent",
                    y="Count",
                    title="📞 Intent Distribution",
                    text="Count"
                )
                st.plotly_chart(fig_intent, use_container_width=True)

            with colD:
                customer_count = df["customer_name"].value_counts().head(10).reset_index()
                customer_count.columns = ["Customer", "Call Count"]

                fig_customer = px.bar(
                    customer_count,
                    x="Customer",
                    y="Call Count",
                    title="🏆 Top Customers by Call Count",
                    text="Call Count"
                )
                st.plotly_chart(fig_customer, use_container_width=True)

            st.divider()

            st.subheader("🔍 Retargeting Customer Details")

            selected_segment = st.selectbox(
                "Select Retargeting Segment",
                ["All"] + sorted(df["retargeting_segment"].unique().tolist())
            )

            selected_sentiment = st.selectbox(
                "Select Sentiment",
                ["All"] + sorted(df["sentiment"].unique().tolist())
            )

            filtered_df = df.copy()

            if selected_segment != "All":
                filtered_df = filtered_df[
                    filtered_df["retargeting_segment"] == selected_segment
                ]

            if selected_sentiment != "All":
                filtered_df = filtered_df[
                    filtered_df["sentiment"] == selected_sentiment
                ]

            st.write(f"Showing **{len(filtered_df)}** matching customers/calls")

            display_columns = [
                "customer_name",
                "phone_number",
                "sentiment",
                "retargeting_segment",
                "intent_category",
                "transcript",
                "analysis"
            ]

            available_columns = [col for col in display_columns if col in filtered_df.columns]

            st.dataframe(
                filtered_df[available_columns],
                use_container_width=True
            )

            csv = filtered_df.to_csv(index=False)

            st.download_button(
                label="Download Filtered Retargeting List CSV",
                data=csv,
                file_name="filtered_retargeting_customers.csv",
                mime="text/csv"
            )

        else:
            st.info("No dashboard data available yet. Analyze and save a call first.")

    except Exception as e:
        st.error("Unable to load dashboard.")
        st.exception(e)
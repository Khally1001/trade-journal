import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from streamlit_calendar import calendar
from datetime import date


if os.path.exists("Trades_Journal.csv"):
  df=  pd.read_csv("Trades_Journal.csv")
  df["Date"] = pd.to_datetime(df["Date"])
else:
   df=pd.DataFrame(columns=["Date",
    "Pair",
    "Bias",
    "Session",
    "Result",
    "Risk",
    "Final RR",
    "Reasoning Behind Trade"]) 
df["Reasoning Behind Trade"] = (
    df["Reasoning Behind Trade"].fillna("").astype(str)
)

# Page layout — this must be near the beginning of your app
st.set_page_config(
    page_title="Trade Journal",
    layout="wide"
)

# Reduce the empty space above the page content
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            max-width: 100%;
        }
        h3 {
                padding-top: 0;
                margin-top: 0;
        }   
        iframe {
            margin-bottom: -3rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Trade Journal")

# Prepare dates
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Remember the date selected on the calendar
if "selected_trade_date" not in st.session_state:
    st.session_state.selected_trade_date = date.today()

# Count how many trades were recorded each day
trade_counts = (
    df.dropna(subset=["Date"])
      .groupby(df["Date"].dt.date)
      .size()
) # This creates a Series where the index is the date and the value is the count of trades for that date

# Give the calendar an event for each day with trades
calendar_events = [
    {
        "title": f"{count} trade(s)",
        "start": trade_date.isoformat(),
        "allDay": True
    }
    for trade_date, count in trade_counts.items()
]

# Display the full monthly calendar
calendar_result = calendar(
    events=calendar_events,
    options={
    "initialView": "dayGridMonth",
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth",
    },
    "timeZone": "UTC",
    "height": "auto",
},
    callbacks=["dateClick"],
    key="trade_calendar"
)

# Update the selected date when you click a day
if calendar_result and calendar_result.get("callback") == "dateClick":
    clicked_date = calendar_result["dateClick"]["date"]
    st.session_state.selected_trade_date = pd.to_datetime(
        clicked_date
    ).date()

# Show the trades for the selected day
selected_date = st.session_state.selected_trade_date

st.subheader(f"Trades for {selected_date.strftime('%d %B %Y')}")

daily_trades = df[df["Date"].dt.date == selected_date]

if daily_trades.empty:
    st.info("No trades recorded for this day.")
else:
    st.dataframe(daily_trades, width="stretch")

for col in ["Pair", "Bias", "Session", "Result"]:
    df[col] = df[col].astype("string")
wins=(df["Result"]=="Win").sum()
total = df["Result"].isin(["Win", "Loss"]).sum()
win_rate = (wins / total) * 100 if total else 0


st.title("Trade Journal",text_alignment="center")

left, right = st.columns([3,1])
with right:
  fig, ax = plt.subplots(figsize=(2, 1))
  fig.patch.set_facecolor("none")
  ax.pie(
      [win_rate, 100 - win_rate],
      colors=["green", "red"],
      startangle=90,
      wedgeprops={"width": 0.15}
  )

  ax.text(
      0, 0, f"{win_rate:.0f}%",
      ha="center", va="center", fontsize=13,color="white", fontweight="bold"
  )

  ax.set_title("Win Rate", fontsize=10,color="white", fontweight="bold")
  ax.axis("equal")

  st.pyplot(fig)
  plt.close(fig)

with left:
  edited_df=st.data_editor(df,num_rows="dynamic",
  column_config={"Date":st.column_config.DateColumn("Date",format="MM/DD/YY"),
                  "Pair":st.column_config.SelectboxColumn("Pair",options=["EURUSD","AUDUSD","USDCAD"]),
                  "Bias":st.column_config.SelectboxColumn("Bias",options=["Bullish","Bearish"]),
                  "Session":st.column_config.SelectboxColumn("Session",options=["Asia","London","NY AM","NY PM"]),
                  "Result":st.column_config.SelectboxColumn("Result",options=["Win","Loss"]),
                  "Risk":st.column_config.NumberColumn("Risk", min_value=0.0, max_value=100.0,step=0.1,format="%.1f%%"),
                  "Final RR":st.column_config.NumberColumn( "Final RR",min_value=-100.0,max_value=100.0,step=0.1,format="%.1fR"),
                  "Reasoning Behind Trade":st.column_config.TextColumn("Reasoning Behind Trade",max_chars=1000)},
                  
                  width="stretch")
  
if st.button("Save trades"):
  

    edited_df.to_csv("Trades_Journal.csv", index=False)
    st.success("Trades saved!")

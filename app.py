import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

def fetch_states():
    url = "https://publiclibraries.com/state/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    states = {
        a.text.strip(): a["href"]
        for a in soup.select(".states-list a")
    }
    return states

def fetch_libraries(state_url):
    response = requests.get(state_url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    data = []
    table = soup.find("table", class_="library-list")
    if table:
        rows = table.find_all("tr")[1:]
        for row in rows:
            cols = [col.text.strip() for col in row.find_all("td")]
            if len(cols) == 5:
                data.append(cols)
    
    return pd.DataFrame(data, columns=["City", "Library", "Address", "Zip", "Phone"])

st.title("Public Libraries in the US")
st.markdown("Select a state to view its public libraries.")

states = fetch_states()
state_name = st.selectbox("Select a State", list(states.keys()))

if state_name:
    df = fetch_libraries(states[state_name])
    
    if not df.empty:
        st.write("### Library Details")
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode("utf-8")
        json = df.to_json(orient="records").encode("utf-8")
        excel_buffer = pd.ExcelWriter("libraries.xlsx", engine="xlsxwriter")
        df.to_excel(excel_buffer, index=False)
        excel_buffer.close()
        
        st.download_button("Download CSV", csv, "libraries.csv", "text/csv")
        st.download_button("Download JSON", json, "libraries.json", "application/json")
        st.download_button("Download Excel", open("libraries.xlsx", "rb"), "libraries.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.write("No libraries found for this state.")
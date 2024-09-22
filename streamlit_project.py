import streamlit as st
import pandas as pd
import json
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt
import seaborn as sns
import ast

st.title ("Euros 2024 shot and heat map")

st.subheader("Filter to any team/player to see shots taken!")

df = pd.read_csv('euros_2024_shot_map.csv')
df = df[df['type'] == 'Shot'].reset_index(drop=True)

df['location'] = df['location'].apply(json.loads)

def filter_data(df: pd.DataFrame, team: str, player: str):
    if team:
        df = df[df['team'] == team]
    if player:
        df = df[df['player'] == player]
    return df

def plot_shots(df, ax, pitch):
    for x in df.to_dict(orient='records'):
        pitch.scatter(
            x=float(x['location'][0]),
            y=float(x['location'][1]),
            ax=ax,
            s=1000 * x['shot_statsbomb_xg'],
            color='green' if x['shot_outcome'] == 'Goal' else 'white',
            edgecolors='black',
            alpha=1 if x['type'] == 'goal' else .5,
            zorder=2 if x['type'] == 'goal' else 1
        )

    # Add a heatmap
    pitch.kdeplot(
        df['location'].apply(lambda x: x[0]),
        df['location'].apply(lambda x: x[1]),
        ax=ax,
        cmap='YlOrRd',
        shade=True,
        shade_lowest=False,
        alpha=0.3,
        zorder=0
    )

# Add this new section for total goals and top scorers
st.subheader("Tournament Statistics")

# Move the team selection before the statistics display
team = st.selectbox("Select a team", ["All Teams"] + sorted(df['team'].unique().tolist()))

# Calculate total goals
if team == "All Teams":
    total_goals = df[df['shot_outcome'] == 'Goal'].shape[0]
    goals_df = df[df['shot_outcome'] == 'Goal']
else:
    total_goals = df[(df['team'] == team) & (df['shot_outcome'] == 'Goal')].shape[0]
    goals_df = df[(df['team'] == team) & (df['shot_outcome'] == 'Goal')]

# Get top scorers
top_scorers = goals_df.groupby('player').size().sort_values(ascending=False).head(5)

# Create two columns
col1, col2 = st.columns(2)

# Display total goals
with col1:
    if team == "All Teams":
        st.metric("Total Goals in Tournament", total_goals)
    else:
        st.metric(f"Total Goals for {team}", total_goals)

# Display top scorers
with col2:
    if team == "All Teams":
        st.write("Top Scorers Overall")
    else:
        st.write(f"Top Scorers for {team}")
    top_scorers_df = pd.DataFrame({'Goals': top_scorers}).reset_index()
    top_scorers_df.columns = ['Player', 'Goals']
    st.table(top_scorers_df)

# Player selection (update to filter based on selected team)
if team == "All Teams":
    player = st.selectbox("Select a player", ["All Players"] + sorted(df['player'].unique().tolist()))
else:
    player = st.selectbox("Select a player", ["All Players"] + sorted(df[df['team'] == team]['player'].unique().tolist()))

# Filter data based on selections
def filter_data(df, team, player):
    if team != "All Teams":
        df = df[df['team'] == team]
    if player != "All Players":
        df = df[df['player'] == player]
    return df

filtered_df = filter_data(df, team, player)

pitch = VerticalPitch(pitch_type='statsbomb', line_zorder=2, pitch_color='#f0f0f0', line_color='black', half=True)
fig, ax = pitch.draw(figsize=(10, 10))
plot_shots(filtered_df, ax, pitch)
st.pyplot(fig)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json
from datetime import timedelta

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IPL XI Selector",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main { background-color: #0a0e1a; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1117 0%, #161b27 100%); border-right: 1px solid #1e2d45; }
[data-testid="stSidebar"] * { color: #e0e6f0 !important; }

.hero-banner {
    background: linear-gradient(135deg, #1a237e 0%, #0d47a1 40%, #01579b 100%);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '🏏';
    position: absolute; right: 40px; top: 50%; transform: translateY(-50%);
    font-size: 80px; opacity: 0.15;
}
.hero-title { font-size: 2.4rem; font-weight: 900; color: #ffffff; margin: 0 0 8px 0; }
.hero-sub { font-size: 1rem; color: #90caf9; margin: 0; }

.metric-card {
    background: linear-gradient(135deg, #111827 0%, #1a2235 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.metric-val { font-size: 2rem; font-weight: 800; color: #60a5fa; }
.metric-label { font-size: 0.78rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px; }

.section-header {
    font-size: 1.1rem; font-weight: 700; color: #93c5fd;
    border-left: 3px solid #3b82f6; padding-left: 12px;
    margin: 24px 0 14px 0;
}

.player-card {
    background: #111827;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.player-name { font-weight: 700; color: #e2e8f0; font-size: 0.95rem; }
.player-role { font-size: 0.75rem; color: #64748b; }
.player-stat { font-size: 0.85rem; color: #60a5fa; font-weight: 600; }

.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-left: 6px;
}
.badge-wk   { background: #1e3a5f; color: #60a5fa; }
.badge-bat  { background: #1a3a1a; color: #4ade80; }
.badge-ar   { background: #3a2a1a; color: #fb923c; }
.badge-bowl { background: #3a1a1a; color: #f87171; }
.badge-ov   { background: #2a1a3a; color: #c084fc; }

.risk-safe    { background: #14532d; color: #4ade80; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
.risk-monitor { background: #713f12; color: #fbbf24; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
.risk-rest    { background: #7f1d1d; color: #f87171; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }

.venue-stat-box {
    background: #0d1117;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}
.venue-stat-val { font-size: 1.6rem; font-weight: 800; color: #60a5fa; }
.venue-stat-lbl { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }

.warning-box {
    background: #1c1a0a;
    border: 1px solid #854d0e;
    border-radius: 8px;
    padding: 10px 14px;
    color: #fbbf24;
    font-size: 0.82rem;
    margin: 8px 0;
}
.info-box {
    background: #0a1628;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 10px 14px;
    color: #93c5fd;
    font-size: 0.82rem;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    bat_match    = pd.read_csv("data/bat_match.csv", parse_dates=["date"])
    bowl_match   = pd.read_csv("data/bowl_match.csv", parse_dates=["date"])
    bat_overall  = pd.read_csv("data/bat_overall.csv")
    bowl_overall = pd.read_csv("data/bowl_overall.csv")
    venue_avg    = pd.read_csv("data/venue_avg.csv")
    venue_phase  = pd.read_csv("data/venue_phase.csv")
    pvb          = pd.read_csv("data/player_venue_bat.csv")
    pvbow        = pd.read_csv("data/player_venue_bowl.csv")
    workload     = pd.read_csv("data/workload.csv", parse_dates=["date"])
    phase_bat    = pd.read_csv("data/phase_bat.csv")
    squads       = pd.read_csv("data/squads_clean.csv")
    venues       = pd.read_csv("data/venues.csv")
    field        = pd.read_csv("data/fielding_stats.csv")
    with open("data/bowling_style.json") as f:
        bowl_style = json.load(f)
    all_matches  = pd.read_csv("data/all_matches.csv", parse_dates=["date"])
    team_h2h     = pd.read_csv("data/team_h2h.csv")
    team_perf    = pd.read_csv("data/team_performance.csv")
    venue_5yr    = pd.read_csv("data/venue_stats_5yr.csv")
    points_all   = pd.read_csv("data/points_all_seasons.csv")
    return (bat_match, bowl_match, bat_overall, bowl_overall,
            venue_avg, venue_phase, pvb, pvbow, workload, phase_bat,
            squads, venues, field, bowl_style,
            all_matches, team_h2h, team_perf, venue_5yr, points_all)

(bat_match, bowl_match, bat_overall, bowl_overall,
 venue_avg, venue_phase, pvb, pvbow, workload, phase_bat,
 squads, venues, field, bowl_style,
 all_matches, team_h2h, team_perf, venue_5yr, points_all) = load_data()

TEAM_COLORS = {
    'MI': '#004BA0', 'CSK': '#F4AC00', 'KKR': '#3A225D', 'RCB': '#EC1C24',
    'GT': '#1B2133', 'RR': '#EA1A85', 'SRH': '#F7A721', 'PBKS': '#AAAAAA',
    'DC': '#0078BC', 'LSG': '#A0E8FF',
}
TEAMS = sorted(squads['team_abbrev'].dropna().unique().tolist())

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_form_batting(player, n=5):
    return bat_match[bat_match['striker'] == player].sort_values('date').tail(n)

def get_form_bowling(player, n=5):
    return bowl_match[bowl_match['bowler'] == player].sort_values('date').tail(n)

def get_workload_flags(team, ref_date=None):
    if ref_date is None:
        ref_date = workload['date'].max()
    w = workload[workload['bowling_team'] == team].copy()
    result = []
    for bowler, grp in w.groupby('bowler'):
        grp = grp.sort_values('date')
        b7  = grp[grp['date'] >= ref_date - timedelta(days=7)]['balls_bowled'].sum()
        b14 = grp[grp['date'] >= ref_date - timedelta(days=14)]['balls_bowled'].sum()
        b28 = grp[grp['date'] >= ref_date - timedelta(days=28)]['balls_bowled'].sum()
        ov7, ov14, ov28 = b7/6, b14/6, b28/6
        if ov7 >= 16 or ov28 >= 55:
            flag = 'rest'
        elif ov7 >= 12 or ov28 >= 45:
            flag = 'monitor'
        else:
            flag = 'safe'
        result.append({
            'bowler': bowler,
            'overs_7d': round(ov7, 1),
            'overs_14d': round(ov14, 1),
            'overs_28d': round(ov28, 1),
            'flag': flag
        })
    return pd.DataFrame(result).sort_values('overs_28d', ascending=False)

def risk_badge(flag):
    emoji = "🟢" if flag == "safe" else "🟡" if flag == "monitor" else "🔴"
    return '<span class="risk-' + flag + '">' + emoji + ' ' + flag.upper() + '</span>'

def score_player(player, role, venue, opponent):
    score = 0
    reasons = []
    if role in ['Batter', 'Wicket Keeper', 'All Rounder']:
        ob = bat_overall[bat_overall['striker'] == player]
        if not ob.empty:
            sr  = ob.iloc[0]['strike_rate']
            avg = ob.iloc[0]['average']
            score += min(sr / 150 * 40, 40)
            score += min(avg / 40 * 30, 30)
            reasons.append("SR " + str(round(sr)) + ", Avg " + str(round(avg, 1)))
        vb = pvb[(pvb['striker'] == player) & (pvb['venue'] == venue)]
        if not vb.empty and vb.iloc[0]['innings'] >= 2:
            v_sr = vb.iloc[0]['sr']
            score += 10 if v_sr > 140 else (5 if v_sr > 110 else 0)
            reasons.append("Venue SR " + str(round(v_sr)))
    if role in ['Bowler', 'All Rounder']:
        ob = bowl_overall[bowl_overall['bowler'] == player]
        if not ob.empty:
            eco  = ob.iloc[0]['economy']
            wkts = ob.iloc[0]['total_wickets']
            score += min((12 - eco) / 4 * 30, 30)
            score += min(wkts / 15 * 30, 30)
            reasons.append("Eco " + str(round(eco, 1)) + ", Wkts " + str(int(wkts)))
        vbow = pvbow[(pvbow['bowler'] == player) & (pvbow['venue'] == venue)]
        if not vbow.empty and vbow.iloc[0]['innings'] >= 2:
            v_eco = vbow.iloc[0]['economy']
            score += 8 if v_eco < 8 else (4 if v_eco < 9.5 else 0)
    return round(score, 1), " | ".join(reasons)

def pick_xi(team, opponent, venue):
    squad = squads[squads['team_abbrev'] == team].copy()
    wl    = get_workload_flags(team)
    rest_players = wl[wl['flag'] == 'rest']['bowler'].tolist()

    scored = []
    for _, row in squad.iterrows():
        player      = row['player']
        role        = row['role']
        is_overseas = row['nationality'] == 'Overseas'
        if player in rest_players:
            continue
        s, reasons = score_player(player, role, venue, opponent)
        scored.append({
            'player': player, 'role': role,
            'is_overseas': is_overseas,
            'score': s, 'reasons': reasons,
            'nationality': row['nationality']
        })

    df = pd.DataFrame(scored).sort_values('score', ascending=False)

    xi = []
    overseas_count = 0
    role_counts = {'Wicket Keeper': 0, 'Batter': 0, 'All Rounder': 0, 'Bowler': 0}

    for _, r in df[df['role'] == 'Wicket Keeper'].iterrows():
        if role_counts['Wicket Keeper'] < 1:
            xi.append(r); role_counts['Wicket Keeper'] += 1
            if r['is_overseas']: overseas_count += 1
            break

    for _, r in df[df['role'] == 'Batter'].iterrows():
        if role_counts['Batter'] >= 4: break
        if r['is_overseas'] and overseas_count >= 4: continue
        xi.append(r); role_counts['Batter'] += 1
        if r['is_overseas']: overseas_count += 1

    for _, r in df[df['role'] == 'All Rounder'].iterrows():
        if role_counts['All Rounder'] >= 2: break
        if r['is_overseas'] and overseas_count >= 4: continue
        xi.append(r); role_counts['All Rounder'] += 1
        if r['is_overseas']: overseas_count += 1

    for _, r in df[df['role'] == 'Bowler'].iterrows():
        if len(xi) >= 11: break
        if r['is_overseas'] and overseas_count >= 4: continue
        xi.append(r); role_counts['Bowler'] += 1
        if r['is_overseas']: overseas_count += 1

    remaining = df[~df['player'].isin([x['player'] for x in xi])]
    for _, r in remaining.iterrows():
        if len(xi) >= 11: break
        if r['is_overseas'] and overseas_count >= 4: continue
        xi.append(r)
        if r['is_overseas']: overseas_count += 1

    return pd.DataFrame(xi[:11]).reset_index(drop=True), df

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏏 IPL XI Selector")
    st.markdown("---")
    page = st.radio("Navigation", [
        "🏠 Home",
        "⚡ XI Selector",
        "📊 Form Analysis",
        "🏟️ Venue Intelligence",
        "💪 Workload Monitor",
    ])
    st.markdown("---")
    st.markdown(
        "<small style='color:#475569'>Data: IPL 2022–2026<br>Tool for IPL 2027 planning</small>",
        unsafe_allow_html=True
    )

page = page.split(" ", 1)[1]

# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
if page == "Home":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">IPL XI Selector</div>
        <div class="hero-sub">Data-driven playing XI decision tool · 2022–2026 team data · 2026 player data · Built for IPL 2027</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("<div class='metric-card'><div class='metric-val'>" + str(len(all_matches)) + "</div><div class='metric-label'>Matches (2022–2026)</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='metric-card'><div class='metric-val'>177</div><div class='metric-label'>Batters Tracked (2026)</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='metric-card'><div class='metric-val'>127</div><div class='metric-label'>Bowlers Tracked (2026)</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='metric-card'><div class='metric-val'>" + str(venue_5yr['venue'].nunique()) + "</div><div class='metric-label'>Venues Covered</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Season Highlights — IPL 2026</div>", unsafe_allow_html=True)
    h1, h2, h3 = st.columns(3)
    highlights = [
        ("🟠 Orange Cap", "Vaibhav Sooryavanshi", "RR · 776 runs · SR 237"),
        ("🟣 Purple Cap", "Kagiso Rabada",         "GT · 29 wickets · Eco 9.48"),
        ("🏆 Champions",  "Royal Challengers Bengaluru", "Def. Gujarat Titans in Final"),
    ]
    for col, (title, name, sub) in zip([h1, h2, h3], highlights):
        with col:
            st.markdown(
                "<div class='metric-card' style='text-align:left'>"
                "<div style='color:#64748b;font-size:0.75rem;margin-bottom:4px'>" + title + "</div>"
                "<div style='color:#e2e8f0;font-weight:700;font-size:1rem'>" + name + "</div>"
                "<div style='color:#60a5fa;font-size:0.8rem;margin-top:4px'>" + sub + "</div>"
                "</div>",
                unsafe_allow_html=True
            )

    st.markdown("<div class='section-header'>Points Table by Season</div>", unsafe_allow_html=True)
    season_pick = st.selectbox("Select Season", sorted(points_all['season'].unique(), reverse=True), key="home_season")
    pt_disp = points_all[points_all['season'] == season_pick].sort_values('points', ascending=False).copy()
    pt_disp = pt_disp[['team', 'played', 'wins', 'losses', 'points', 'win_pct']]
    pt_disp.columns = ['Team', 'Played', 'Wins', 'Losses', 'Points', 'Win %']
    st.dataframe(pt_disp, use_container_width=True, hide_index=True)

    st.markdown("<div class='section-header'>Team Win % Trend (2022–2026)</div>", unsafe_allow_html=True)
    trend_fig = px.line(
        points_all, x='season', y='win_pct', color='team',
        markers=True,
        labels={'win_pct': 'Win %', 'season': 'Season'},
    )
    trend_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e2e8f0', height=380,
        xaxis=dict(gridcolor='#1e2d45', dtick=1),
        yaxis=dict(gridcolor='#1e2d45'),
        legend=dict(orientation='h', yanchor='bottom', y=-0.4),
        margin=dict(l=0, r=0, t=10, b=10)
    )
    st.plotly_chart(trend_fig, use_container_width=True)

    st.markdown("<div class='section-header'>Tool Features</div>", unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    features = [
        ("⚡", "XI Selector",       "Pick your best 11 for any match based on form, venue & opponent"),
        ("📊", "Form Analysis",     "Rolling 5-match performance trends for any player (2026)"),
        ("🏟️", "Venue Intel",       "5-year ground records, avg scores and bat-first win rates"),
        ("💪", "Workload Monitor",  "7/14/28-day bowling load with traffic-light risk flags"),
    ]
    for col, (icon, title, desc) in zip([f1, f2, f3, f4], features):
        with col:
            st.markdown(
                "<div class='metric-card' style='text-align:left;padding:18px'>"
                "<div style='font-size:1.8rem'>" + icon + "</div>"
                "<div style='color:#e2e8f0;font-weight:700;margin:8px 0 4px'>" + title + "</div>"
                "<div style='color:#64748b;font-size:0.78rem'>" + desc + "</div>"
                "</div>",
                unsafe_allow_html=True
            )

# ══════════════════════════════════════════════════════════════════════════════
# XI SELECTOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "XI Selector":
    st.markdown("## ⚡ XI Selector")
    st.markdown("Select your franchise, opponent, and venue to generate the optimal playing XI.")

    c1, c2, c3 = st.columns(3)
    with c1:
        team = st.selectbox("Your Franchise", TEAMS, key="xi_team")
    with c2:
        opp_options = [t for t in TEAMS if t != team]
        opponent = st.selectbox("Opponent", opp_options, key="xi_opp")
    with c3:
        venue_options = sorted(venue_5yr['venue'].unique().tolist())
        venue = st.selectbox("Match Venue", venue_options, key="xi_venue")

    if st.button("🏏 Generate XI", type="primary", use_container_width=True):
        xi_df, full_squad = pick_xi(team, opponent, venue)

        # ── Venue summary ─────────────────────────────────────────────────────
        vdata  = venue_5yr[venue_5yr['venue'] == venue]
        vphase = venue_phase[venue_phase['venue'] == venue]

        st.markdown("<div class='section-header'>🏟️ Venue Summary (2022–2026)</div>", unsafe_allow_html=True)
        vc1, vc2, vc3, vc4 = st.columns(4)
        avg_score      = str(int(vdata['avg_first_innings'].values[0])) if not vdata.empty else "N/A"
        matches_played = str(int(vdata['matches'].values[0]))           if not vdata.empty else "0"
        bat_first_pct  = (str(vdata['bat_first_pct'].values[0]) + "%") if not vdata.empty else "N/A"
        pp_rr          = vphase[vphase['phase'] == 'Powerplay']['run_rate'].values
        pp_display     = str(pp_rr[0]) if len(pp_rr) else "N/A"

        with vc1:
            st.markdown("<div class='venue-stat-box'><div class='venue-stat-val'>" + avg_score + "</div><div class='venue-stat-lbl'>Avg 1st Innings (5yr)</div></div>", unsafe_allow_html=True)
        with vc2:
            st.markdown("<div class='venue-stat-box'><div class='venue-stat-val'>" + matches_played + "</div><div class='venue-stat-lbl'>Matches Played</div></div>", unsafe_allow_html=True)
        with vc3:
            st.markdown("<div class='venue-stat-box'><div class='venue-stat-val'>" + bat_first_pct + "</div><div class='venue-stat-lbl'>Bat-First Win Rate</div></div>", unsafe_allow_html=True)
        with vc4:
            st.markdown("<div class='venue-stat-box'><div class='venue-stat-val'>" + pp_display + "</div><div class='venue-stat-lbl'>Powerplay RR (2026)</div></div>", unsafe_allow_html=True)

        # ── Team H2H inline ───────────────────────────────────────────────────
        h2h_row = team_h2h[(team_h2h['team_a'] == team) & (team_h2h['team_b'] == opponent)]
        if not h2h_row.empty:
            hr = h2h_row.iloc[0]
            st.markdown(
                "<div class='info-box'>🆚 <strong>" + team + "</strong> vs <strong>" + opponent +
                "</strong> (2022–2026): " + str(int(hr['wins'])) + "W - " + str(int(hr['losses'])) +
                "L from " + str(int(hr['matches'])) + " matches (" + str(hr['win_pct']) + "% win rate)</div>",
                unsafe_allow_html=True
            )

        # ── Recommended XI ────────────────────────────────────────────────────
        st.markdown("<div class='section-header'>✅ Recommended Playing XI</div>", unsafe_allow_html=True)

        role_badge = {'Wicket Keeper': 'wk', 'Batter': 'bat', 'All Rounder': 'ar', 'Bowler': 'bowl'}
        role_label = {'Wicket Keeper': 'WK', 'Batter': 'BAT', 'All Rounder': 'AR', 'Bowler': 'BOWL'}

        wl_flags = get_workload_flags(team)

        for i, row in xi_df.iterrows():
            badge_type = role_badge.get(row['role'], 'bat')
            role_text  = role_label.get(row['role'], '')
            ov_badge   = '<span class="badge badge-ov">OS</span>' if row['is_overseas'] else ""
            stat_hint  = str(row['reasons']) if row['reasons'] else "Squad player"

            wl_info = wl_flags[wl_flags['bowler'] == row['player']]
            if not wl_info.empty:
                wl_tag = risk_badge(wl_info.iloc[0]['flag'])
            else:
                wl_tag = ""

            card = (
                '<div class="player-card">'
                    '<div>'
                        '<span style="color:#64748b;font-size:0.8rem;margin-right:8px">#' + str(i + 1) + '</span>'
                        '<span class="player-name">' + str(row['player']) + '</span>'
                        '<span class="badge badge-' + badge_type + '">' + role_text + '</span>'
                        + ov_badge +
                    '</div>'
                    '<div style="display:flex;align-items:center;gap:12px">'
                        '<span style="color:#475569;font-size:0.78rem">' + stat_hint + '</span>'
                        + wl_tag +
                        '<span class="player-stat">Score: ' + str(row['score']) + '</span>'
                    '</div>'
                '</div>'
            )
            st.markdown(card, unsafe_allow_html=True)

        overseas_in_xi = int(xi_df['is_overseas'].sum())
        st.markdown(
            "<div class='info-box'>ℹ️ Overseas players in XI: <strong>" + str(overseas_in_xi) +
            "/4</strong> · Players ranked by composite form + venue + score</div>",
            unsafe_allow_html=True
        )

        # ── Score chart ───────────────────────────────────────────────────────
        st.markdown("<div class='section-header'>📊 Selection Score Breakdown</div>", unsafe_allow_html=True)
        fig = px.bar(
            xi_df.sort_values('score'),
            x='score', y='player', orientation='h', color='role',
            color_discrete_map={
                'Batter': '#4ade80', 'Bowler': '#f87171',
                'All Rounder': '#fb923c', 'Wicket Keeper': '#60a5fa'
            },
            labels={'score': 'Selection Score', 'player': ''},
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0', height=380,
            legend_title_text='Role',
            xaxis=dict(gridcolor='#1e2d45'),
            yaxis=dict(gridcolor='#1e2d45'),
            margin=dict(l=0, r=0, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Full squad rankings ───────────────────────────────────────────────
        with st.expander("📋 View Full Squad Rankings"):
            disp = full_squad[['player', 'role', 'nationality', 'score', 'reasons']].copy()
            disp.columns = ['Player', 'Role', 'Nationality', 'Score', 'Key Stats']
            st.dataframe(disp, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# FORM ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Form Analysis":
    st.markdown("## 📊 Form Analysis")
    st.markdown("Rolling performance over last N matches for any player (IPL 2026).")

    fa1, fa2 = st.columns([2, 1])
    with fa1:
        all_players = sorted(bat_overall['striker'].unique().tolist())
        player = st.selectbox("Select Player", all_players)
    with fa2:
        n_matches = st.slider("Matches window", 3, 10, 5)

    tab1, tab2 = st.tabs(["🏏 Batting Form", "🎳 Bowling Form"])

    with tab1:
        form = get_form_batting(player, n_matches)
        if form.empty:
            st.info("No batting data found for this player.")
        else:
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.markdown("<div class='metric-card'><div class='metric-val'>" + str(form['runs'].sum()) + "</div><div class='metric-label'>Total Runs</div></div>", unsafe_allow_html=True)
            with m2: st.markdown("<div class='metric-card'><div class='metric-val'>" + str(round(form['sr'].mean())) + "</div><div class='metric-label'>Avg Strike Rate</div></div>", unsafe_allow_html=True)
            with m3: st.markdown("<div class='metric-card'><div class='metric-val'>" + str(form['runs'].max()) + "</div><div class='metric-label'>High Score</div></div>", unsafe_allow_html=True)
            with m4: st.markdown("<div class='metric-card'><div class='metric-val'>" + str(len(form)) + "</div><div class='metric-label'>Innings</div></div>", unsafe_allow_html=True)

            st.markdown("<div class='section-header'>Runs per Match</div>", unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=form['date'].dt.strftime('%d %b'), y=form['runs'],
                marker_color='#3b82f6', name='Runs',
                text=form['runs'], textposition='outside',
            ))
            fig.add_trace(go.Scatter(
                x=form['date'].dt.strftime('%d %b'), y=form['sr'],
                mode='lines+markers', name='Strike Rate', yaxis='y2',
                line=dict(color='#f59e0b', width=2), marker=dict(size=8),
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e2e8f0', height=320,
                yaxis=dict(title='Runs', gridcolor='#1e2d45'),
                yaxis2=dict(title='Strike Rate', overlaying='y', side='right', gridcolor='#1e2d45'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02),
                margin=dict(l=0, r=0, t=10, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("<div class='section-header'>Phase Breakdown</div>", unsafe_allow_html=True)
            ph = phase_bat[phase_bat['striker'] == player]
            if not ph.empty:
                fig2 = px.bar(
                    ph, x='phase', y='sr', color='phase',
                    color_discrete_map={'Powerplay': '#4ade80', 'Middle': '#60a5fa', 'Death': '#f87171'},
                    labels={'sr': 'Strike Rate', 'phase': 'Phase'}, text='sr'
                )
                fig2.update_traces(texttemplate='%{text:.0f}', textposition='outside')
                fig2.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#e2e8f0', height=260, showlegend=False,
                    xaxis=dict(gridcolor='#1e2d45'), yaxis=dict(gridcolor='#1e2d45'),
                    margin=dict(l=0, r=0, t=10, b=10)
                )
                st.plotly_chart(fig2, use_container_width=True)

            with st.expander("📋 Match-by-match log"):
                log = form[['date', 'batting_team', 'venue', 'runs', 'balls', 'sr', 'fours', 'sixes']].copy()
                log['date'] = log['date'].dt.strftime('%d %b %Y')
                log.columns = ['Date', 'Team', 'Venue', 'Runs', 'Balls', 'SR', '4s', '6s']
                st.dataframe(log, use_container_width=True, hide_index=True)

    with tab2:
        form_b = get_form_bowling(player, n_matches)
        if form_b.empty:
            st.info("No bowling data found for this player.")
        else:
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.markdown("<div class='metric-card'><div class='metric-val'>" + str(form_b['wickets'].sum()) + "</div><div class='metric-label'>Wickets</div></div>", unsafe_allow_html=True)
            with m2: st.markdown("<div class='metric-card'><div class='metric-val'>" + str(round(form_b['economy'].mean(), 1)) + "</div><div class='metric-label'>Avg Economy</div></div>", unsafe_allow_html=True)
            with m3: st.markdown("<div class='metric-card'><div class='metric-val'>" + str(round(form_b['overs'].sum(), 1)) + "</div><div class='metric-label'>Overs Bowled</div></div>", unsafe_allow_html=True)
            with m4: st.markdown("<div class='metric-card'><div class='metric-val'>" + str(len(form_b)) + "</div><div class='metric-label'>Innings</div></div>", unsafe_allow_html=True)

            st.markdown("<div class='section-header'>Wickets & Economy per Match</div>", unsafe_allow_html=True)
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(
                x=form_b['date'].dt.strftime('%d %b'), y=form_b['wickets'],
                marker_color='#f87171', name='Wickets',
                text=form_b['wickets'], textposition='outside'
            ))
            fig3.add_trace(go.Scatter(
                x=form_b['date'].dt.strftime('%d %b'), y=form_b['economy'],
                mode='lines+markers', name='Economy', yaxis='y2',
                line=dict(color='#fbbf24', width=2), marker=dict(size=8)
            ))
            fig3.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e2e8f0', height=320,
                yaxis=dict(title='Wickets', gridcolor='#1e2d45'),
                yaxis2=dict(title='Economy', overlaying='y', side='right', gridcolor='#1e2d45'),
                legend=dict(orientation='h', yanchor='bottom', y=1.02),
                margin=dict(l=0, r=0, t=10, b=10)
            )
            st.plotly_chart(fig3, use_container_width=True)

            with st.expander("📋 Match-by-match log"):
                log = form_b[['date', 'bowling_team', 'venue', 'wickets', 'overs', 'economy', 'runs_given']].copy()
                log['date'] = log['date'].dt.strftime('%d %b %Y')
                log.columns = ['Date', 'Team', 'Venue', 'Wickets', 'Overs', 'Economy', 'Runs Given']
                st.dataframe(log, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# VENUE INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Venue Intelligence":
    st.markdown("## 🏟️ Venue Intelligence")
    st.markdown("Ground-specific records across 2022–2026, with 2026 phase-level detail.")

    venue_options = sorted(venue_5yr['venue'].unique().tolist())
    sel_venue = st.selectbox("Select Venue", venue_options)

    vdata  = venue_5yr[venue_5yr['venue'] == sel_venue]
    vphase = venue_phase[venue_phase['venue'] == sel_venue]

    if not vdata.empty:
        vd = vdata.iloc[0]
        v1, v2, v3, v4 = st.columns(4)
        with v1:
            st.markdown("<div class='venue-stat-box'><div class='venue-stat-val'>" + str(int(vd['avg_first_innings'])) + "</div><div class='venue-stat-lbl'>Avg 1st Innings (5yr)</div></div>", unsafe_allow_html=True)
        with v2:
            st.markdown("<div class='venue-stat-box'><div class='venue-stat-val'>" + str(int(vd['matches'])) + "</div><div class='venue-stat-lbl'>Matches (2022–2026)</div></div>", unsafe_allow_html=True)
        with v3:
            st.markdown("<div class='venue-stat-box'><div class='venue-stat-val'>" + str(vd['bat_first_pct']) + "%</div><div class='venue-stat-lbl'>Bat-First Win Rate</div></div>", unsafe_allow_html=True)
        with v4:
            pp = vphase[vphase['phase'] == 'Powerplay']['run_rate'].values
            pp_val = str(pp[0]) if len(pp) else "N/A"
            st.markdown("<div class='venue-stat-box'><div class='venue-stat-val'>" + pp_val + "</div><div class='venue-stat-lbl'>Powerplay RR (2026)</div></div>", unsafe_allow_html=True)

        st.markdown(
            "<div class='info-box'>ℹ️ Bat first has won <strong>" + str(int(vd['bat_first_wins'])) +
            "</strong> of " + str(int(vd['matches'])) + " matches here, chasing has won <strong>" +
            str(int(vd['chase_wins'])) + "</strong> — across 2022–2026.</div>",
            unsafe_allow_html=True
        )

    if not vphase.empty:
        st.markdown("<div class='section-header'>Run Rate by Phase (2026)</div>", unsafe_allow_html=True)
        fig = px.bar(
            vphase, x='phase', y='run_rate', color='phase',
            color_discrete_map={'Powerplay': '#4ade80', 'Middle': '#60a5fa', 'Death': '#f87171'},
            labels={'run_rate': 'Run Rate (per over)', 'phase': 'Phase'}, text='run_rate'
        )
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0', height=300, showlegend=False,
            xaxis=dict(gridcolor='#1e2d45'),
            yaxis=dict(title='Run Rate', gridcolor='#1e2d45'),
            margin=dict(l=0, r=0, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>Top Batters at This Venue (2026)</div>", unsafe_allow_html=True)
    vb = pvb[pvb['venue'] == sel_venue].sort_values('runs', ascending=False).head(10)
    if vb.empty:
        st.info("No player-venue batting data available.")
    else:
        fig2 = px.bar(
            vb, x='striker', y='runs', color='sr',
            color_continuous_scale=['#1e3a5f', '#60a5fa'],
            labels={'runs': 'Runs', 'striker': 'Player', 'sr': 'Strike Rate'}, text='runs'
        )
        fig2.update_traces(textposition='outside')
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0', height=320,
            xaxis=dict(gridcolor='#1e2d45', tickangle=-30),
            yaxis=dict(gridcolor='#1e2d45'),
            margin=dict(l=0, r=0, t=10, b=10),
            coloraxis_colorbar=dict(title='SR')
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>Top Bowlers at This Venue (2026)</div>", unsafe_allow_html=True)
    vbow = pvbow[pvbow['venue'] == sel_venue].sort_values('wickets', ascending=False).head(10)
    if vbow.empty:
        st.info("No player-venue bowling data available.")
    else:
        fig3 = px.bar(
            vbow, x='bowler', y='wickets', color='economy',
            color_continuous_scale=['#4ade80', '#f87171'],
            labels={'wickets': 'Wickets', 'bowler': 'Bowler', 'economy': 'Economy'}, text='wickets'
        )
        fig3.update_traces(textposition='outside')
        fig3.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0', height=320,
            xaxis=dict(gridcolor='#1e2d45', tickangle=-30),
            yaxis=dict(gridcolor='#1e2d45'),
            margin=dict(l=0, r=0, t=10, b=10),
            coloraxis_colorbar=dict(title='Economy')
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown(
        "<div class='info-box'>ℹ️ Venue scoring/win-rate stats span 5 seasons (2022–2026). Player-level records are from 2026 only.</div>",
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════════════════════════════════════════
# WORKLOAD MONITOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Workload Monitor":
    st.markdown("## 💪 Workload Monitor")
    st.markdown("Bowling load over the last 7, 14, and 28 days with risk flags for medical staff.")

    wl_team = st.selectbox("Select Team", TEAMS)
    wl_df   = get_workload_flags(wl_team)

    if wl_df.empty:
        st.info("No bowling workload data for this team.")
    else:
        safe_n    = int((wl_df['flag'] == 'safe').sum())
        monitor_n = int((wl_df['flag'] == 'monitor').sum())
        rest_n    = int((wl_df['flag'] == 'rest').sum())

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<div class='metric-card'><div class='metric-val' style='color:#4ade80'>" + str(safe_n) + "</div><div class='metric-label'>🟢 Safe</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='metric-card'><div class='metric-val' style='color:#fbbf24'>" + str(monitor_n) + "</div><div class='metric-label'>🟡 Monitor</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown("<div class='metric-card'><div class='metric-val' style='color:#f87171'>" + str(rest_n) + "</div><div class='metric-label'>🔴 Rest</div></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-header'>Bowler Workload Table</div>", unsafe_allow_html=True)

        for _, row in wl_df.iterrows():
            flag_html = risk_badge(row['flag'])
            card = (
                '<div class="player-card">'
                    '<div>'
                        '<span class="player-name">' + str(row['bowler']) + '</span>'
                    '</div>'
                    '<div style="display:flex;align-items:center;gap:16px">'
                        '<span style="color:#94a3b8;font-size:0.8rem">7d: <strong style="color:#e2e8f0">' + str(row['overs_7d']) + ' ov</strong></span>'
                        '<span style="color:#94a3b8;font-size:0.8rem">14d: <strong style="color:#e2e8f0">' + str(row['overs_14d']) + ' ov</strong></span>'
                        '<span style="color:#94a3b8;font-size:0.8rem">28d: <strong style="color:#e2e8f0">' + str(row['overs_28d']) + ' ov</strong></span>'
                        + flag_html +
                    '</div>'
                '</div>'
            )
            st.markdown(card, unsafe_allow_html=True)

        st.markdown("<div class='section-header'>28-Day Overs Bowled</div>", unsafe_allow_html=True)
        wl_sorted = wl_df.sort_values('overs_28d', ascending=True)
        colors = ['#f87171' if f == 'rest' else '#fbbf24' if f == 'monitor' else '#4ade80' for f in wl_sorted['flag']]
        fig = go.Figure(go.Bar(
            x=wl_sorted['overs_28d'], y=wl_sorted['bowler'],
            orientation='h', marker_color=colors,
            text=wl_sorted['overs_28d'], textposition='outside',
        ))
        fig.add_vline(x=45, line_dash='dash', line_color='#fbbf24', annotation_text='Monitor (45 ov)')
        fig.add_vline(x=55, line_dash='dash', line_color='#f87171', annotation_text='Rest (55 ov)')
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0', height=max(300, len(wl_df) * 32),
            xaxis=dict(title='Overs in last 28 days', gridcolor='#1e2d45'),
            yaxis=dict(gridcolor='#1e2d45'),
            margin=dict(l=0, r=0, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            "<div class='info-box'>ℹ️ <strong>Thresholds:</strong> "
            "🟢 Safe = &lt;12 ov/7d and &lt;45 ov/28d · "
            "🟡 Monitor = 12–16 ov/7d or 45–55 ov/28d · "
            "🔴 Rest = 16+ ov/7d or 55+ ov/28d</div>",
            unsafe_allow_html=True
        )
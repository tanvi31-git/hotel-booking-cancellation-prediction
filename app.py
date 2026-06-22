import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Hotel Bookings Analysis",
    page_icon="🏨",
    layout="wide"
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        border: 1px solid #e9ecef;
    }
    .insight-box {
        background: #fff8e1;
        border-left: 4px solid #f59e0b;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
        font-size: 0.875rem;
    }
    .anomaly-box {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 0.75rem 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    import os
    # works both locally and on Streamlit Cloud
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "hotel_bookings_featured.csv")
    df = pd.read_csv(path)
    month_order = ['January','February','March','April','May','June',
                   'July','August','September','October','November','December']
    df['arrival_date_month'] = pd.Categorical(df['arrival_date_month'], categories=month_order, ordered=True)
    df = df[df['market_segment'] != 'Undefined']
    return df

df = load_data()

# ── Sidebar filters ────────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/hotel.png", width=60)
st.sidebar.title("Filters")

hotel_filter = st.sidebar.multiselect(
    "Hotel type",
    options=df['hotel'].unique().tolist(),
    default=df['hotel'].unique().tolist()
)

year_filter = st.sidebar.multiselect(
    "Year",
    options=sorted(df['arrival_date_year'].unique().tolist()),
    default=sorted(df['arrival_date_year'].unique().tolist())
)

season_filter = st.sidebar.multiselect(
    "Season",
    options=df['season'].unique().tolist(),
    default=df['season'].unique().tolist()
)

filtered = df[
    df['hotel'].isin(hotel_filter) &
    df['arrival_date_year'].isin(year_filter) &
    df['season'].isin(season_filter)
]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**{len(filtered):,}** bookings selected")
st.sidebar.markdown("Built by **Tanvi Adke** · [GitHub](#) · [LinkedIn](#)")

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🏨 Hotel Booking Cancellation Analysis")
st.caption("Exploratory data analysis on 87K+ hotel bookings | Kaggle dataset | Python · pandas · Plotly · Streamlit")

tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔍 Deep Dive", "⚠️ Key Anomaly"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    total = len(filtered)
    cancelled = filtered['is_canceled'].sum()
    cancel_rate = cancelled / total * 100 if total else 0
    revenue = filtered['estimated_revenue'].sum()
    avg_adr = filtered['adr'].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total bookings", f"{total:,}")
    c2.metric("Cancellation rate", f"{cancel_rate:.1f}%", delta=f"-{cancelled:,} bookings", delta_color="inverse")
    c3.metric("Estimated revenue", f"₹{revenue/1e7:.2f} Cr")
    c4.metric("Avg daily rate", f"₹{avg_adr:,.0f}")

    st.markdown("---")

    # Monthly revenue
    st.subheader("Revenue trend by month")
    monthly = (
        filtered.groupby('arrival_date_month', observed=True)['estimated_revenue']
        .sum().reset_index()
    )
    monthly.columns = ['Month', 'Revenue']
    fig_month = px.bar(
        monthly, x='Month', y='Revenue',
        color='Revenue',
        color_continuous_scale='Blues',
        labels={'Revenue': 'Estimated Revenue (₹)'},
        text=monthly['Revenue'].apply(lambda x: f"₹{x/1e5:.0f}L")
    )
    fig_month.update_traces(textposition='outside')
    fig_month.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis_tickformat=',.0f',
        height=380,
        margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig_month, use_container_width=True)
    st.markdown('<div class="insight-box">💡 <b>Insight:</b> July–August drives nearly 38% of annual revenue. Winter months (Nov–Feb) are significantly weaker — hotels should push off-season promotions.</div>', unsafe_allow_html=True)

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Cancellation by hotel type")
        hotel_cancel = filtered.groupby('hotel')['is_canceled'].mean().reset_index()
        hotel_cancel.columns = ['Hotel', 'Cancel Rate']
        hotel_cancel['Cancel Rate %'] = (hotel_cancel['Cancel Rate'] * 100).round(1)
        fig_hotel = px.bar(
            hotel_cancel, x='Hotel', y='Cancel Rate %',
            color='Hotel', color_discrete_sequence=['#3b82f6', '#f59e0b'],
            text='Cancel Rate %'
        )
        fig_hotel.update_traces(texttemplate='%{text}%', textposition='outside')
        fig_hotel.update_layout(
            showlegend=False, height=300,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig_hotel, use_container_width=True)

    with col_right:
        st.subheader("Revenue share by season")
        season_rev = filtered.groupby('season')['estimated_revenue'].sum().reset_index()
        fig_season = px.pie(
            season_rev, names='season', values='estimated_revenue',
            color_discrete_sequence=['#1d4ed8', '#3b82f6', '#93c5fd', '#dbeafe'],
            hole=0.5
        )
        fig_season.update_traces(textinfo='label+percent')
        fig_season.update_layout(
            height=300, margin=dict(t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_season, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Cancellation rate by customer type")
    cust = filtered.groupby('customer_type')['is_canceled'].mean().reset_index()
    cust.columns = ['Customer Type', 'Cancel Rate']
    cust['Cancel Rate %'] = (cust['Cancel Rate'] * 100).round(1)
    cust = cust.sort_values('Cancel Rate %', ascending=True)
    fig_cust = px.bar(
        cust, x='Cancel Rate %', y='Customer Type', orientation='h',
        color='Cancel Rate %', color_continuous_scale='Reds',
        text='Cancel Rate %'
    )
    fig_cust.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_cust.update_layout(
        coloraxis_showscale=False, height=280,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10)
    )
    st.plotly_chart(fig_cust, use_container_width=True)
    st.markdown('<div class="insight-box">💡 <b>Insight:</b> Transient customers cancel at 30.1% — nearly 3x higher than Group bookings (9.8%). Loyalty programmes targeting transient guests could significantly reduce revenue loss.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Cancellation rate by lead time")
    lead_order = ['Last Minute', 'Short Term', 'Medium Term', 'Long Term']
    lead = filtered.groupby('lead_time_group')['is_canceled'].mean().reset_index()
    lead.columns = ['Lead Time', 'Cancel Rate']
    lead['Cancel Rate %'] = (lead['Cancel Rate'] * 100).round(1)
    lead['Lead Time'] = pd.Categorical(lead['Lead Time'], categories=lead_order, ordered=True)
    lead = lead.sort_values('Lead Time')
    fig_lead = px.line(
        lead, x='Lead Time', y='Cancel Rate %',
        markers=True, line_shape='spline',
        color_discrete_sequence=['#3b82f6']
    )
    fig_lead.update_traces(marker=dict(size=12), line=dict(width=3))
    fig_lead.update_layout(
        height=280, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(range=[0, 50], ticksuffix='%'),
        margin=dict(t=10, b=10)
    )
    st.plotly_chart(fig_lead, use_container_width=True)
    st.markdown('<div class="insight-box">💡 <b>Insight:</b> Last-minute bookings cancel at only 18.6% vs 39.7% for long-term bookings. Hotels could offer last-minute discounts to fill rooms more reliably.</div>', unsafe_allow_html=True)

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Repeat vs new guests")
        guest = filtered.groupby('guest_type')['is_canceled'].mean().reset_index()
        guest.columns = ['Guest Type', 'Cancel Rate']
        guest['Cancel Rate %'] = (guest['Cancel Rate'] * 100).round(1)
        fig_guest = px.bar(
            guest, x='Guest Type', y='Cancel Rate %',
            color='Guest Type', color_discrete_sequence=['#f97316', '#86efac'],
            text='Cancel Rate %'
        )
        fig_guest.update_traces(texttemplate='%{text}%', textposition='outside')
        fig_guest.update_layout(
            showlegend=False, height=300,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[0, 35], ticksuffix='%'),
            margin=dict(t=10, b=10)
        )
        st.plotly_chart(fig_guest, use_container_width=True)
        st.markdown('<div class="insight-box">💡 Repeat guests cancel <b>3.7x less</b> than new guests (7.7% vs 28.3%).</div>', unsafe_allow_html=True)

    with col_b:
        st.subheader("Top 10 booking countries")
        top_countries = (
            filtered.groupby('country').size()
            .reset_index(name='Bookings')
            .sort_values('Bookings', ascending=False)
            .head(10)
        )
        fig_ctry = px.bar(
            top_countries, x='Bookings', y='country', orientation='h',
            color='Bookings', color_continuous_scale='Blues'
        )
        fig_ctry.update_layout(
            coloraxis_showscale=False, height=300,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            yaxis_title='', margin=dict(t=10, b=10)
        )
        st.plotly_chart(fig_ctry, use_container_width=True)

    st.markdown("---")
    st.subheader("Market segment — volume vs cancellation rate")
    mkt = filtered.groupby('market_segment').agg(
        Bookings=('is_canceled', 'count'),
        Cancel_Rate=('is_canceled', 'mean')
    ).reset_index()
    mkt['Cancel Rate %'] = (mkt['Cancel_Rate'] * 100).round(1)
    fig_mkt = px.scatter(
        mkt, x='Bookings', y='Cancel Rate %',
        size='Bookings', color='market_segment',
        hover_name='market_segment',
        labels={'market_segment': 'Segment'},
        size_max=60
    )
    fig_mkt.update_layout(
        height=350, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        yaxis_ticksuffix='%', margin=dict(t=10, b=10)
    )
    st.plotly_chart(fig_mkt, use_container_width=True)
    st.markdown('<div class="insight-box">💡 <b>Insight:</b> Online TA has the highest volume (51K bookings) but also a high 35.4% cancel rate — the riskiest segment by revenue impact.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — KEY ANOMALY
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("⚠️ The Non-Refundable Deposit Paradox")
    st.markdown("""
    This is the most counterintuitive finding in the entire dataset — and a great talking point in interviews.
    """)

    dep = filtered.groupby('deposit_type')['is_canceled'].mean().reset_index()
    dep.columns = ['Deposit Type', 'Cancel Rate']
    dep['Cancel Rate %'] = (dep['Cancel Rate'] * 100).round(1)

    fig_dep = px.bar(
        dep, x='Deposit Type', y='Cancel Rate %',
        color='Deposit Type',
        color_discrete_sequence=['#86efac', '#fde68a', '#f87171'],
        text='Cancel Rate %'
    )
    fig_dep.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_dep.update_layout(
        showlegend=False, height=350,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(range=[0, 115], ticksuffix='%'),
        margin=dict(t=10, b=40)
    )
    st.plotly_chart(fig_dep, use_container_width=True)

    st.markdown('<div class="anomaly-box">🚨 <b>Non-refundable bookings cancel at 94.7%</b> — nearly 4x higher than no-deposit bookings (26.7%). This seems completely backward.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Why does this happen?")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **The data explanation:**

        In hotel industry data, a booking marked `reservation_status = Canceled` with a `Non Refund` deposit
        doesn't always mean the guest cancelled voluntarily.

        It means the booking was **closed as cancelled in the system** — but the hotel still **collected the deposit**.

        These are often:
        - **No-shows** recorded as cancellations
        - **OTA (Online Travel Agency) bookings** where the guest cancelled on the OTA platform but the hotel records it as a system cancellation
        - **Fraudulent or accidental bookings** where the guest never intended to stay
        """)
    with col2:
        st.markdown("""
        **The business interpretation:**

        Non-refundable rates attract **price-sensitive customers** who book speculatively — they grab the cheapest rate available without firm travel plans.

        This creates a paradox: the policy designed to *reduce* cancellation risk actually *attracts* the guests most likely to cancel.

        **ML implication:** `deposit_type` is one of the strongest predictors in a cancellation model — but you must understand *why*, or you'll misinterpret its direction.

        **Interview talking point:** Always question whether a feature's relationship with the target is causal or a data artefact.
        """)

    st.markdown("---")
    dep_vol = filtered.groupby('deposit_type').agg(
        Bookings=('is_canceled','count'),
        Cancellations=('is_canceled','sum')
    ).reset_index()
    dep_vol['Completed'] = dep_vol['Bookings'] - dep_vol['Cancellations']
    st.subheader("Volume breakdown by deposit type")
    fig_vol = go.Figure(data=[
        go.Bar(name='Completed stays', x=dep_vol['deposit_type'], y=dep_vol['Completed'], marker_color='#86efac'),
        go.Bar(name='Cancelled', x=dep_vol['deposit_type'], y=dep_vol['Cancellations'], marker_color='#f87171'),
    ])
    fig_vol.update_layout(
        barmode='stack', height=320,
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10)
    )
    st.plotly_chart(fig_vol, use_container_width=True)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import database
import certificate
import qrcode
import io
import os
import csv
from datetime import datetime

st.set_page_config(page_title="EventHub Portal", page_icon="🎫", layout="wide")

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    color: white;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stSelectbox label { color: #f6d365 !important; font-weight: 600; }

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px; padding: 24px; color: white;
    text-align: center; box-shadow: 0 8px 32px rgba(102,126,234,0.4);
    margin-bottom: 8px;
}
.metric-card h2 { font-size: 2.5rem; font-weight: 700; margin: 0; }
.metric-card p  { font-size: 0.9rem; opacity: 0.85; margin: 4px 0 0; }

.metric-green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); box-shadow: 0 8px 32px rgba(17,153,142,0.4); }
.metric-orange { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); box-shadow: 0 8px 32px rgba(245,87,108,0.4); }
.metric-blue  { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); box-shadow: 0 8px 32px rgba(79,172,254,0.4); }

.event-card {
    background: white; border-radius: 12px; padding: 20px;
    border-left: 5px solid #667eea; margin-bottom: 16px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}
.ticket-box {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 16px; padding: 28px; color: white;
    border: 2px dashed #c8a951; text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.page-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px; padding: 20px 28px; color: white; margin-bottom: 28px;
}
.page-header h2 { margin: 0; font-size: 1.6rem; }
.page-header p  { margin: 4px 0 0; opacity: 0.85; font-size: 0.9rem; }

.stButton > button {
    background: linear-gradient(90deg, #667eea, #764ba2);
    color: white; border: none; border-radius: 8px;
    padding: 10px 24px; font-weight: 600; transition: all 0.2s;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102,126,234,0.5); }

div[data-testid="stForm"] {
    background: #f8f9ff; border-radius: 12px;
    padding: 24px; border: 1px solid #e8e8f0;
}
</style>
""", unsafe_allow_html=True)

database.init_db()

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎫 EventHub")
    st.markdown("---")
    page = st.selectbox("Navigate", [
        "📊 Dashboard",
        "📅 All Events",
        "➕ Create Event",
        "🎟️ Book Ticket",
        "🔍 My Registrations",
        "👥 Admin: Participants",
        "🏆 Admin: Certificates",
        "✏️ Admin: Manage Events",
    ])
    st.markdown("---")
    st.markdown("**Quick Stats**")
    stats = database.get_dashboard_stats()
    st.metric("Total Events", stats["total_events"])
    st.metric("Total Registrations", stats["total_registrations"])

# ── Helper ──────────────────────────────────────────────────────────────────
def header(title, subtitle=""):
    st.markdown(f"""
    <div class="page-header">
        <h2>{title}</h2>
        <p>{subtitle}</p>
    </div>""", unsafe_allow_html=True)

CATEGORIES = ["Conference", "Workshop", "Seminar", "College Fest", "Concert", "Hackathon", "Sports", "Other"]

# ════════════════════════════════════════════════════════════════════
#  PAGES
# ════════════════════════════════════════════════════════════════════

# ─── 1. DASHBOARD ──────────────────────────────────────────────────
if page == "📊 Dashboard":
    header("📊 Dashboard", "Real-time overview of your events and registrations")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><h2>{stats["total_events"]}</h2><p>Total Events</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card metric-green"><h2>{stats["total_registrations"]}</h2><p>Total Registrations</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card metric-orange"><h2>{stats["upcoming_events"]}</h2><p>Upcoming Events</p></div>', unsafe_allow_html=True)
    with c4:
        avg = round(stats["total_registrations"] / max(stats["total_events"], 1), 1)
        st.markdown(f'<div class="metric-card metric-blue"><h2>{avg}</h2><p>Avg Registrations/Event</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Top Events by Registrations")
        if stats["top_events"]:
            df_top = pd.DataFrame(stats["top_events"], columns=["Event", "Registrations"])
            fig = px.bar(df_top, x="Registrations", y="Event", orientation='h',
                         color="Registrations", color_continuous_scale="Viridis")
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=280)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No events yet.")

    with col2:
        st.subheader("🎯 Registrations by Category")
        if stats["category_data"]:
            df_cat = pd.DataFrame(stats["category_data"], columns=["Category", "Count"])
            fig2 = px.pie(df_cat, names="Category", values="Count",
                          color_discrete_sequence=px.colors.sequential.Plasma_r, hole=0.4)
            fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=280)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data yet.")

    st.subheader("📈 Registration Trend")
    if stats["reg_trend"]:
        df_trend = pd.DataFrame(stats["reg_trend"], columns=["Date", "Count"])
        fig3 = px.area(df_trend, x="Date", y="Count",
                       color_discrete_sequence=["#667eea"], title="Daily Registrations")
        fig3.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=250)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No registrations recorded yet.")

    st.subheader("📊 Capacity Utilisation")
    if stats["capacity_data"]:
        df_cap = pd.DataFrame(stats["capacity_data"], columns=["Event", "Capacity", "Registered"])
        df_cap["Available"] = df_cap["Capacity"] - df_cap["Registered"]
        df_cap["Fill %"] = (df_cap["Registered"] / df_cap["Capacity"] * 100).round(1)
        fig4 = go.Figure(data=[
            go.Bar(name="Registered", x=df_cap["Event"], y=df_cap["Registered"], marker_color="#667eea"),
            go.Bar(name="Available",  x=df_cap["Event"], y=df_cap["Available"],  marker_color="#e8e8f0"),
        ])
        fig4.update_layout(barmode='stack', margin=dict(l=0, r=0, t=10, b=0), height=280)
        st.plotly_chart(fig4, use_container_width=True)

# ─── 2. ALL EVENTS ─────────────────────────────────────────────────
elif page == "📅 All Events":
    header("📅 All Events", "Browse all available events")
    search = st.text_input("🔍 Search events", placeholder="Type event name or location…")
    cat_filter = st.selectbox("Filter by Category", ["All"] + CATEGORIES)
    events = database.get_events()

    if events:
        for e in events:
            eid, ename, edate, eloc, edesc, ecap, ecat, ecreated = e
            if search and search.lower() not in ename.lower() and search.lower() not in (eloc or "").lower():
                continue
            if cat_filter != "All" and ecat != cat_filter:
                continue
            parts = database.get_participants(eid)
            filled = len(parts)
            pct = int(filled / ecap * 100) if ecap else 0
            badge_color = "#38ef7d" if pct < 70 else "#f5a623" if pct < 100 else "#f5576c"
            st.markdown(f"""
            <div class="event-card">
                <b style="font-size:1.15rem">{ename}</b>
                <span style="float:right;background:{badge_color};color:white;
                      border-radius:20px;padding:3px 12px;font-size:0.8rem">
                  {ecat or 'General'}
                </span><br>
                📅 {edate} &nbsp;|&nbsp; 📍 {eloc} &nbsp;|&nbsp;
                👥 {filled}/{ecap} seats ({pct}% full)<br>
                <small style="color:#555">{edesc}</small>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No events found. Create one from the sidebar!")

# ─── 3. CREATE EVENT ───────────────────────────────────────────────
elif page == "➕ Create Event":
    header("➕ Create New Event", "Add a new event to the portal")
    with st.form("create_event_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Event Name *")
            date = st.date_input("Event Date *")
            location = st.text_input("Location *")
        with col2:
            category = st.selectbox("Category", CATEGORIES)
            capacity = st.number_input("Max Capacity", min_value=1, value=100)
        description = st.text_area("Description *", height=100)
        submitted = st.form_submit_button("🚀 Create Event")
        if submitted:
            if name and location and description:
                database.add_event(name, str(date), location, description, capacity, category)
                st.success(f"✅ Event **{name}** created successfully!")
                st.balloons()
            else:
                st.warning("Please fill all required fields.")

# ─── 4. BOOK TICKET ────────────────────────────────────────────────
elif page == "🎟️ Book Ticket":
    header("🎟️ Book Your Ticket", "Register and get your e-ticket instantly")
    events = database.get_events()
    if not events:
        st.info("No events available. Check back soon!")
    else:
        event_dict = {f"{e[1]} — {e[2]} | {e[3]}": e[0] for e in events}
        selected_str = st.selectbox("Select Event", list(event_dict.keys()))
        selected_id = event_dict[selected_str]
        ev = database.get_event(selected_id)

        col1, col2 = st.columns([2, 1])
        with col1:
            with st.form("booking_form"):
                name  = st.text_input("Full Name *")
                email = st.text_input("Email Address *")
                phone = st.text_input("Phone Number")
                submitted = st.form_submit_button("🎫 Book Ticket")
                if submitted:
                    if name and email:
                        ok, result = database.register_participant(selected_id, name, email, phone)
                        if ok:
                            st.success("🎉 Booking confirmed!")
                            st.balloons()
                            # Show e-ticket
                            reg_id = result
                            qr_data = f"EventHub|{ev[1]}|{name}|{email}|REG-{reg_id:05d}"
                            qr_img = qrcode.make(qr_data)
                            buf = io.BytesIO()
                            qr_img.save(buf, format="PNG")
                            st.markdown(f"""
                            <div class="ticket-box">
                                <h2>🎫 E-TICKET</h2>
                                <h3 style="color:#f6d365">{ev[1]}</h3>
                                <p>📅 {ev[2]} &nbsp;|&nbsp; 📍 {ev[3]}</p>
                                <p>👤 <b>{name}</b> &nbsp;|&nbsp; 📧 {email}</p>
                                <p style="color:#a8edea;font-size:1.2rem">Booking ID: REG-{reg_id:05d}</p>
                            </div>""", unsafe_allow_html=True)
                            st.image(buf.getvalue(), caption="Scan QR at entry", width=180)
                        else:
                            st.error(result)
                    else:
                        st.warning("Name and email are required.")
        with col2:
            parts = database.get_participants(selected_id)
            filled = len(parts)
            pct = filled / ev[5] * 100 if ev[5] else 0
            st.markdown(f"""
            <div class="event-card">
                <b>{ev[1]}</b><br>
                📅 {ev[2]}<br>📍 {ev[3]}<br>
                🎯 {ev[6] or 'General'}<br><br>
                <b>Availability</b><br>
                {filled} / {ev[5]} seats booked
            </div>""", unsafe_allow_html=True)
            st.progress(min(pct / 100, 1.0))

# ─── 5. MY REGISTRATIONS ───────────────────────────────────────────
elif page == "🔍 My Registrations":
    header("🔍 My Registrations", "Look up all your event registrations")
    email = st.text_input("Enter your email address")
    if st.button("Search") and email:
        rows = database.get_registrations_by_email(email)
        if rows:
            st.success(f"Found {len(rows)} registration(s).")
            for r in rows:
                reg_id, ename, edate, eloc, pname, reg_at = r
                st.markdown(f"""
                <div class="event-card">
                    <b>{ename}</b> &nbsp;
                    <span style="background:#667eea;color:white;border-radius:10px;
                          padding:2px 10px;font-size:0.8rem">REG-{reg_id:05d}</span><br>
                    📅 {edate} &nbsp;|&nbsp; 📍 {eloc}<br>
                    👤 {pname} &nbsp;|&nbsp; 🕒 Registered: {reg_at}
                </div>""", unsafe_allow_html=True)
        else:
            st.warning("No registrations found for this email.")

# ─── 6. ADMIN: PARTICIPANTS ────────────────────────────────────────
elif page == "👥 Admin: Participants":
    header("👥 Participant Management", "View and export participant lists")
    events = database.get_events()
    if not events:
        st.info("No events available.")
    else:
        event_dict = {f"{e[1]} ({e[2]})": e[0] for e in events}
        sel_str = st.selectbox("Select Event", list(event_dict.keys()))
        sel_id  = event_dict[sel_str]
        ev = database.get_event(sel_id)
        participants = database.get_participants(sel_id)

        col1, col2, col3 = st.columns(3)
        col1.metric("Registered", len(participants))
        col2.metric("Capacity", ev[5])
        col3.metric("Available Seats", ev[5] - len(participants))

        if participants:
            df = pd.DataFrame(participants,
                              columns=["ID", "Event ID", "Name", "Email", "Phone", "Registered At"])
            df = df.drop(columns=["Event ID"])

            search_p = st.text_input("🔍 Search participant")
            if search_p:
                df = df[df["Name"].str.contains(search_p, case=False) |
                        df["Email"].str.contains(search_p, case=False)]
            st.dataframe(df.set_index("ID"), use_container_width=True)

            # CSV export
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Export CSV", csv_data,
                               file_name=f"{ev[1].replace(' ','_')}_participants.csv",
                               mime="text/csv")

            # PDF report
            if st.button("📄 Generate PDF Report"):
                path = certificate.generate_participant_report_pdf(ev[1], ev[2], participants)
                with open(path, "rb") as f:
                    st.download_button("⬇️ Download PDF Report", f.read(),
                                       file_name=os.path.basename(path),
                                       mime="application/pdf")
        else:
            st.info("No participants registered yet.")

# ─── 7. ADMIN: CERTIFICATES ────────────────────────────────────────
elif page == "🏆 Admin: Certificates":
    header("🏆 Certificate Generation", "Generate and download participation certificates")
    events = database.get_events()
    if not events:
        st.info("No events available.")
    else:
        event_dict = {f"{e[1]} ({e[2]})": e[0] for e in events}
        sel_str = st.selectbox("Select Event", list(event_dict.keys()))
        sel_id  = event_dict[sel_str]
        ev = database.get_event(sel_id)
        participants = database.get_participants(sel_id)

        if not participants:
            st.info("No participants registered for this event.")
        else:
            tab1, tab2 = st.tabs(["Single Certificate", "Bulk Generate"])
            with tab1:
                p_dict = {p[2]: p for p in participants}
                sel_p = st.selectbox("Select Participant", list(p_dict.keys()))
                if st.button("🏆 Generate Certificate"):
                    p = p_dict[sel_p]
                    try:
                        path = certificate.generate_certificate(p[2], ev[1], ev[2])
                        st.success("Certificate generated!")
                        with open(path, "rb") as f:
                            st.download_button("⬇️ Download Certificate", f.read(),
                                               file_name=os.path.basename(path),
                                               mime="application/pdf")
                    except Exception as ex:
                        st.error(f"Error: {ex}")

            with tab2:
                st.write(f"Generate certificates for all **{len(participants)}** participants.")
                if st.button("🚀 Generate All Certificates"):
                    prog = st.progress(0)
                    generated = []
                    for i, p in enumerate(participants):
                        try:
                            path = certificate.generate_certificate(p[2], ev[1], ev[2])
                            generated.append(path)
                        except Exception:
                            pass
                        prog.progress((i+1) / len(participants))
                    st.success(f"✅ Generated {len(generated)} certificates in the `certificates/` folder!")

# ─── 8. ADMIN: MANAGE EVENTS ───────────────────────────────────────
elif page == "✏️ Admin: Manage Events":
    header("✏️ Manage Events", "Edit or delete existing events")
    events = database.get_events()
    if not events:
        st.info("No events available.")
    else:
        event_dict = {f"{e[1]} ({e[2]})": e[0] for e in events}
        sel_str = st.selectbox("Select Event to Manage", list(event_dict.keys()))
        sel_id  = event_dict[sel_str]
        ev = database.get_event(sel_id)

        tab_edit, tab_del = st.tabs(["✏️ Edit Event", "🗑️ Delete Event"])
        with tab_edit:
            with st.form("edit_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name  = st.text_input("Event Name", value=ev[1])
                    date  = st.date_input("Event Date",
                                          value=datetime.strptime(ev[2], "%Y-%m-%d").date())
                    loc   = st.text_input("Location", value=ev[3] or "")
                with col2:
                    cat   = st.selectbox("Category", CATEGORIES,
                                         index=CATEGORIES.index(ev[6]) if ev[6] in CATEGORIES else 0)
                    cap   = st.number_input("Capacity", min_value=1, value=ev[5])
                desc = st.text_area("Description", value=ev[4] or "", height=100)
                if st.form_submit_button("💾 Save Changes"):
                    database.update_event(sel_id, name, str(date), loc, desc, cap, cat)
                    st.success("✅ Event updated!")
                    st.rerun()

        with tab_del:
            st.warning(f"⚠️ This will permanently delete **{ev[1]}** and all its registrations.")
            confirm = st.checkbox("I understand, delete this event")
            if confirm and st.button("🗑️ Delete Event", type="primary"):
                database.delete_event(sel_id)
                st.success("Event deleted.")
                st.rerun()

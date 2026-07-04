"""Reusable rendering helpers for PawPal's Streamlit UI."""

import html
from datetime import datetime

import streamlit.components.v1 as components
import streamlit as st

from constants import PAGE_BANNERS


def render_page_banner(page_key: str) -> None:
    """Render a page banner image if a matching asset exists."""
    banner_path = PAGE_BANNERS.get(page_key)
    if banner_path and banner_path.exists():
        st.image(str(banner_path), use_container_width=True)


def render_live_clock(note: str | None = None) -> None:
    """Render a small live clock card that updates client-side every second."""
    current = datetime.now()
    initial_time = current.strftime("%I:%M:%S %p").lstrip("0")
    initial_date = current.strftime("%A, %B ") + str(current.day) + current.strftime(", %Y")
    note_html = f"<div class='pp-clock-note'>{html.escape(note)}</div>" if note else ""
    clock_html = f"""
    <style>
      .pp-clock-card {{
        border: 1px solid rgba(151, 167, 196, 0.28);
        border-radius: 10px;
        padding: 12px 14px;
        background: #F7F9FC;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: #102542;
      }}
      .pp-clock-head {{
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        gap: 12px;
        margin-bottom: 8px;
      }}
      .pp-clock-label {{
        font-size: 0.82rem;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        color: #5b6572;
        font-weight: 700;
      }}
      .pp-clock-note {{
        font-size: 0.8rem;
        color: #5b6572;
      }}
      .pp-clock-time {{
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.1;
        color: #102542;
      }}
      .pp-clock-date {{
        margin-top: 2px;
        font-size: 0.94rem;
        color: #5b6572;
      }}
    </style>
    <div class="pp-clock-card">
      <div class="pp-clock-head">
        <div class="pp-clock-label">Live Clock</div>
        {note_html}
      </div>
      <div class="pp-clock-time" id="pp-clock-time">{initial_time}</div>
      <div class="pp-clock-date" id="pp-clock-date">{initial_date}</div>
    </div>
    <script>
      const timeEl = document.getElementById("pp-clock-time");
      const dateEl = document.getElementById("pp-clock-date");
      function updateClock() {{
        const now = new Date();
        const time = now.toLocaleTimeString([], {{ hour: "numeric", minute: "2-digit", second: "2-digit" }});
        const date = now.toLocaleDateString([], {{ weekday: "long", month: "long", day: "numeric", year: "numeric" }});
        timeEl.textContent = time;
        dateEl.textContent = date;
      }}
      updateClock();
      setInterval(updateClock, 1000);
    </script>
    """
    components.html(clock_html, height=150)

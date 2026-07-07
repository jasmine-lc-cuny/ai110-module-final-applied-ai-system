from schedule_views import render_monthly_schedule_page

render_monthly_schedule_page(
    page_icon="🗓️",
    page_title="Clinic Monthly Schedule",
    caption="Browse veterinary visits by month, and drill into any day's full schedule.",
    categories={"veterinary"},
    session_key_prefix="clinic",
    include_reason=True,
)

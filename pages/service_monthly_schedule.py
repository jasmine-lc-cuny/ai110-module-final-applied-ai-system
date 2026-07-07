from schedule_views import render_monthly_schedule_page

SERVICE_CATEGORIES = {"grooming", "sitting", "training", "walking", "special_services"}

render_monthly_schedule_page(
    page_icon="🗓️",
    page_title="Service Monthly Schedule",
    caption="Browse booked services by month, and drill into any day's full schedule.",
    categories=SERVICE_CATEGORIES,
    session_key_prefix="service",
    include_reason=False,
)

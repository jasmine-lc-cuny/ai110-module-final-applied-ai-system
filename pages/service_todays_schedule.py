from schedule_views import render_todays_schedule_page

SERVICE_CATEGORIES = {"grooming", "sitting", "training", "walking", "special_services"}

render_todays_schedule_page(
    page_icon="📅",
    page_title="Service Today's Schedule",
    caption="See today's booked services, priorities, and conflicts, and complete, delete, or reopen tasks.",
    categories=SERVICE_CATEGORIES,
    include_reason=False,
)

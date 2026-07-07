from schedule_views import render_todays_schedule_page

render_todays_schedule_page(
    page_icon="📅",
    page_title="Clinic Today's Schedule",
    caption="See today's veterinary tasks, priorities, and conflicts, and complete, delete, or reopen tasks.",
    categories={"veterinary"},
    include_reason=True,
)

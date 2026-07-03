import streamlit as st
from app_common import render_category_page

# Calls the veterinary logic but styles it as PawPal's master Task page
render_category_page(
    category="veterinary",
    display_name="Veterinary",
    icon="🐾", 
    page_title="🐾 PawPal's Task",
    page_subtitle="Schedule a Task"
)
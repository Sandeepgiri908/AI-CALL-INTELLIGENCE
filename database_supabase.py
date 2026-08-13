import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_call_analysis(customer_name, phone_number, transcript, analysis):
    data = {
        "customer_name": customer_name or "Unknown",
        "phone_number": phone_number or "Unknown",
        "transcript": transcript or "",
        "analysis": str(analysis)
    }

    response = supabase.table("call_analysis").insert(data).execute()
    print("SAVE RESPONSE:", response)
    return response.data

def get_call_history():
    response = supabase.table("call_analysis").select("*").execute()
    print("HISTORY RESPONSE:", response)
    return response.data or []

def get_dashboard_data():
    response = supabase.table("call_analysis").select("*").execute()
    print("DASHBOARD RESPONSE:", response)
    return response.data or []
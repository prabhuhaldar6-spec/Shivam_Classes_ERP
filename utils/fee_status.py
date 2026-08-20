def get_fee_status(supabase_client, class_filter: str = None):
    """Returns a list of dicts with each student's total fee, amount paid
    so far, and remaining balance. Pass class_filter to limit to one class.
    """
    students_query = supabase_client.table("students").select("*")
    if class_filter:
        students_query = students_query.eq("class", class_filter)
    students = students_query.execute().data

    fees = supabase_client.table("fees").select("*").execute().data

    paid_by_student = {}
    for f in fees:
        sid = f["student_id"]
        paid_by_student[sid] = paid_by_student.get(sid, 0) + (f["amount"] or 0)

    rows = []
    for s in students:
        total_fee = s.get("total_fee") or 0
        paid = paid_by_student.get(s["id"], 0)
        rows.append(
            {
                "id": s["id"],
                "full_name": s["full_name"],
                "class": s["class"],
                "total_fee": total_fee,
                "paid": paid,
                "remaining": total_fee - paid,
            }
        )
    return rows

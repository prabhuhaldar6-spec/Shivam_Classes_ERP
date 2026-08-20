from datetime import date
import streamlit as st
from utils.supabase_client import supabase
from utils.supabase_admin_client import supabase_admin
from utils.class_list import CLASS_LIST
from utils.branding import show_header
from utils.generate_receipt import generate_receipt
from utils.fee_status import get_fee_status
from utils import telegram

st.set_page_config(page_title="Admin Dashboard", page_icon="utils/logo.jpg")

# Guard: only logged-in admins can see this page
if st.session_state.get("role") != "admin":
    st.warning("Please log in as an admin (on the main page) to view this dashboard.")
    st.stop()

show_header("🛠️ Admin Dashboard")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "Add Student",
        "All Students",
        "Add Teacher / Parent",
        "All Staff",
        "Fees & Receipts",
        "Link Telegram",
        "Fee Status",
    ]
)

# --- Add Student ---
with tab1:
    with st.form("add_student"):
        full_name = st.text_input("Student full name")
        student_class = st.selectbox("Class", CLASS_LIST)
        total_fee = st.number_input("Total fee for the year (Rs.)", min_value=0.0, step=500.0)
        amount_paid_now = st.number_input(
            "Amount paid now, if any (e.g. admission fee) (Rs.)", min_value=0.0, step=500.0
        )
        payment_month = st.text_input(
            "This payment is for (e.g. 'Registration' or 'August 2026')",
            value="Registration",
        )
        submitted = st.form_submit_button("Add Student")
        if submitted:
            # 1. Create the student record
            new_student = (
                supabase.table("students")
                .insert(
                    {"full_name": full_name, "class": student_class, "total_fee": total_fee}
                )
                .execute()
            )
            student_id = new_student.data[0]["id"]

            result = {
                "full_name": full_name,
                "student_id": student_id,
                "total_fee": total_fee,
                "amount_paid_now": amount_paid_now,
                "payment_month": payment_month,
                "pdf_path": None,
                "receipt_no": None,
                "remaining_val": None,
            }

            # 2. If any amount was paid at registration, record it and generate a receipt
            if amount_paid_now > 0:
                fee_row = (
                    supabase.table("fees")
                    .insert(
                        {
                            "student_id": student_id,
                            "amount": amount_paid_now,
                            "month": payment_month,
                            "paid_on": str(date.today()),
                        }
                    )
                    .execute()
                )
                receipt_no = str(fee_row.data[0]["id"])
                remaining_val = total_fee - amount_paid_now

                pdf_path = generate_receipt(
                    full_name,
                    amount_paid_now,
                    payment_month,
                    receipt_no,
                    total_fee=total_fee,
                    remaining=remaining_val,
                )
                result["pdf_path"] = pdf_path
                result["receipt_no"] = receipt_no
                result["remaining_val"] = remaining_val

            st.session_state["last_added_student"] = result

    # Everything below runs OUTSIDE the form — download_button isn't allowed inside one
    last = st.session_state.get("last_added_student")
    if last:
        st.success(f"Added {last['full_name']}")
        if last["pdf_path"]:
            st.info(f"Remaining balance for {last['full_name']}: Rs. {last['remaining_val']}")
            with open(last["pdf_path"], "rb") as f:
                st.download_button(
                    "Download Registration Receipt PDF",
                    f,
                    file_name=f"receipt_{last['receipt_no']}.pdf",
                    key="download_last_receipt",
                )
            st.caption(
                "Note: this student isn't linked to Telegram yet, so the receipt "
                "wasn't auto-sent — link them in 'Link Telegram' to enable that for next time."
            )

# --- All Students ---
with tab2:
    students = supabase.table("students").select("*").execute()
    st.dataframe(students.data)

    if students.data:
        st.divider()
        st.subheader("Delete a student")
        delete_names = {s["full_name"]: s for s in students.data}
        chosen_delete_name = st.selectbox(
            "Select student to delete", list(delete_names.keys()), key="delete_student_pick"
        )
        confirm_delete_student = st.checkbox(
            f"I confirm I want to permanently delete {chosen_delete_name} "
            "and all their attendance/fee records",
            key="confirm_delete_student",
        )
        if st.button("Delete Student", key="delete_student_btn"):
            if confirm_delete_student:
                student_to_delete = delete_names[chosen_delete_name]
                sid = student_to_delete["id"]
                # Clean up related records first (foreign key references)
                supabase.table("fees").delete().eq("student_id", sid).execute()
                supabase.table("attendance").delete().eq("student_id", sid).execute()
                supabase.table("students").delete().eq("id", sid).execute()
                st.success(f"Deleted {chosen_delete_name} and their related records.")
                st.rerun()
            else:
                st.warning("Please check the confirmation box first.")

# --- Add Teacher / Parent (creates a real login, no need to touch Supabase) ---
with tab3:
    st.write("Create a login for a teacher or parent. They'll use this email/password to sign in.")
    with st.form("add_staff"):
        staff_role = st.selectbox("This person is a", ["teacher", "parent"])
        staff_name = st.text_input("Full name")
        staff_email = st.text_input("Email")
        staff_password = st.text_input("Temporary password", type="password")
        submitted = st.form_submit_button("Create Login")
        if submitted:
            try:
                result = supabase_admin.auth.admin.create_user(
                    {
                        "email": staff_email,
                        "password": staff_password,
                        "email_confirm": True,  # skip email verification step
                    }
                )
                new_user_id = result.user.id
                supabase_admin.table("profiles").insert(
                    {
                        "id": new_user_id,
                        "full_name": staff_name,
                        "role": staff_role,
                    }
                ).execute()
                st.success(f"{staff_role.title()} login created for {staff_name} ({staff_email})")
            except Exception as e:
                st.error(f"Could not create login: {e}")

# --- All Staff ---
with tab4:
    profiles = (
        supabase_admin.table("profiles")
        .select("*")
        .in_("role", ["teacher", "parent"])
        .execute()
    )
    st.dataframe(profiles.data)

    if profiles.data:
        st.divider()
        st.subheader("Remove a teacher or parent login")
        delete_staff = {p["full_name"]: p for p in profiles.data}
        chosen_delete_staff = st.selectbox(
            "Select person to remove", list(delete_staff.keys()), key="delete_staff_pick"
        )
        confirm_delete_staff = st.checkbox(
            f"I confirm I want to permanently remove {chosen_delete_staff}'s login",
            key="confirm_delete_staff",
        )
        if st.button("Delete Login", key="delete_staff_btn"):
            if confirm_delete_staff:
                staff_to_delete = delete_staff[chosen_delete_staff]
                try:
                    supabase_admin.auth.admin.delete_user(staff_to_delete["id"])
                    supabase_admin.table("profiles").delete().eq(
                        "id", staff_to_delete["id"]
                    ).execute()
                    st.success(f"Removed {chosen_delete_staff}'s login.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not remove login: {e}")
            else:
                st.warning("Please check the confirmation box first.")

# --- Fees & Receipts ---
with tab5:
    st.write("Record a fee payment, generate a PDF receipt, and send it on Telegram.")
    all_students = supabase.table("students").select("*").execute().data

    if all_students:
        student_names = {s["full_name"]: s for s in all_students}
        with st.form("record_fee"):
            chosen_name = st.selectbox("Student", list(student_names.keys()))
            amount = st.number_input("Amount paid (Rs.)", min_value=0.0, step=100.0)
            month = st.text_input("Month (e.g. August 2026)")
            submitted = st.form_submit_button("Record Payment & Generate Receipt")
            if submitted:
                student = student_names[chosen_name]

                # 1. Save the payment in Supabase
                fee_row = (
                    supabase.table("fees")
                    .insert(
                        {
                            "student_id": student["id"],
                            "amount": amount,
                            "month": month,
                            "paid_on": str(date.today()),
                        }
                    )
                    .execute()
                )
                receipt_no = str(fee_row.data[0]["id"])

                # 2. Work out the running balance
                status_rows = get_fee_status(supabase)
                this_status = next(
                    (r for r in status_rows if r["id"] == student["id"]), None
                )
                total_fee_val = this_status["total_fee"] if this_status else None
                remaining_val = this_status["remaining"] if this_status else None

                # 3. Generate the PDF
                pdf_path = generate_receipt(
                    chosen_name,
                    amount,
                    month,
                    receipt_no,
                    total_fee=total_fee_val,
                    remaining=remaining_val,
                )

                # 4. Send it on Telegram if this student has a linked chat_id
                chat_id = student.get("telegram_chat_id")
                telegram_sent = False
                telegram_error = None
                if chat_id:
                    try:
                        telegram.send_document(
                            chat_id,
                            pdf_path,
                            caption=f"Fee receipt for {chosen_name} — {month} — Rs. {amount}",
                        )
                        telegram_sent = True
                    except Exception as e:
                        telegram_error = str(e)

                st.session_state["last_fee_record"] = {
                    "chosen_name": chosen_name,
                    "receipt_no": receipt_no,
                    "pdf_path": pdf_path,
                    "remaining_val": remaining_val,
                    "chat_id": chat_id,
                    "telegram_sent": telegram_sent,
                    "telegram_error": telegram_error,
                }

        # Everything below runs OUTSIDE the form — download_button isn't allowed inside one
        last_fee = st.session_state.get("last_fee_record")
        if last_fee:
            st.success(f"Receipt #{last_fee['receipt_no']} generated.")
            if last_fee["remaining_val"] is not None:
                st.info(
                    f"Remaining balance for {last_fee['chosen_name']}: "
                    f"Rs. {last_fee['remaining_val']}"
                )
            with open(last_fee["pdf_path"], "rb") as f:
                st.download_button(
                    "Download Receipt PDF",
                    f,
                    file_name=f"receipt_{last_fee['receipt_no']}.pdf",
                    key="download_last_fee_receipt",
                )
            if last_fee["chat_id"]:
                if last_fee["telegram_sent"]:
                    st.success("Receipt sent on Telegram too.")
                else:
                    st.warning(f"Saved, but could not send on Telegram: {last_fee['telegram_error']}")
            else:
                st.info(
                    f"{last_fee['chosen_name']} isn't linked to Telegram yet — "
                    "link them in the 'Link Telegram' tab to auto-send receipts."
                )
    else:
        st.info("Add students first before recording fees.")

    st.divider()
    st.subheader("Send a payment reminder")
    if all_students:
        reminder_student_name = st.selectbox(
            "Remind which student's parent?", list(student_names.keys()), key="reminder_pick"
        )
        reminder_month = st.text_input("For which month?", key="reminder_month")
        if st.button("Send Reminder on Telegram"):
            student = student_names[reminder_student_name]
            chat_id = student.get("telegram_chat_id")
            if chat_id:
                telegram.send_message(
                    chat_id,
                    f"Reminder: fee payment for {reminder_student_name} "
                    f"({reminder_month}) is due at Shivam Classes. Please pay at your earliest convenience.",
                )
                st.success("Reminder sent.")
            else:
                st.warning(f"{reminder_student_name} isn't linked to Telegram yet.")

# --- Link Telegram ---
with tab6:
    st.write(
        "Ask parents/students to search for your bot on Telegram and send `/start`. "
        "Then click below to see who has messaged it and link them to a student."
    )
    if st.button("Check for new Telegram registrations"):
        registrations = telegram.get_recent_registrations()
        if registrations:
            st.session_state["telegram_registrations"] = registrations
        else:
            st.info("No registrations found yet. Ask the parent/student to message the bot first.")

    registrations = st.session_state.get("telegram_registrations", [])
    if registrations and all_students:
        for reg in registrations:
            label = reg["name"] or reg["username"] or reg["chat_id"]
            with st.form(f"link_{reg['chat_id']}"):
                st.write(f"Telegram user: **{label}** (@{reg['username']})")
                match_student = st.selectbox(
                    "Link to which student?",
                    list(student_names.keys()),
                    key=f"match_{reg['chat_id']}",
                )
                link_submitted = st.form_submit_button("Link")
                if link_submitted:
                    supabase.table("students").update(
                        {"telegram_chat_id": reg["chat_id"]}
                    ).eq("id", student_names[match_student]["id"]).execute()
                    st.success(f"Linked {label} to {match_student}")

# --- Fee Status ---
with tab7:
    st.write("See every student's total fee, amount paid, and remaining balance.")
    class_filter_choice = st.selectbox(
        "Filter by class", ["All classes"] + CLASS_LIST, key="fee_status_class_filter"
    )
    filter_value = None if class_filter_choice == "All classes" else class_filter_choice
    status_rows = get_fee_status(supabase, class_filter=filter_value)

    if status_rows:
        st.dataframe(
            [
                {
                    "Student": r["full_name"],
                    "Class": r["class"],
                    "Total Fee (Rs.)": r["total_fee"],
                    "Paid (Rs.)": r["paid"],
                    "Remaining (Rs.)": r["remaining"],
                }
                for r in status_rows
            ]
        )

        total_remaining = sum(r["remaining"] for r in status_rows)
        st.metric("Total remaining across these students", f"Rs. {total_remaining}")
    else:
        st.info("No students found for this filter.")

    st.divider()
    st.subheader("Update a student's total fee")
    if all_students:
        edit_student_name = st.selectbox(
            "Student", list(student_names.keys()), key="edit_fee_student"
        )
        current = student_names[edit_student_name]
        new_total_fee = st.number_input(
            "New total fee (Rs.)",
            min_value=0.0,
            step=500.0,
            value=float(current.get("total_fee") or 0),
            key="edit_fee_amount",
        )
        if st.button("Update Total Fee"):
            supabase.table("students").update(
                {"total_fee": new_total_fee}
            ).eq("id", current["id"]).execute()
            st.success(f"Updated total fee for {edit_student_name}")

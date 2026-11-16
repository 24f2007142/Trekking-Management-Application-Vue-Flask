from celery import shared_task


from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import render_template

from models import Booking, Trek, User
from sqlalchemy import or_

from email_utils import send_email

import csv
import io

from db import db

def safe_csv_text(value):
    text = str(value)

    if text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text

    return text


@shared_task
def send_daily_reminders():
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    tomorrow = today + timedelta(days=1)

    bookings = (
        Booking.query
        .join(Trek, Booking.trek_id == Trek.id)
        .join(User, Booking.user_id == User.id)
        .filter(
            Booking.status == "confirmed",
            Trek.trek_status == "upcoming",
            Trek.start_date == tomorrow,
            User.approval_status == "approved",
        )
        .all()
    )

    for booking in bookings:
        message = (
            f"Hello {booking.user.username}, "
            f"your trek {booking.trek.trek_name} "
            f"starts tomorrow at {booking.trek.location}. "
            f"You have booked {booking.slots_booked} slot(s)."
        )

        send_email(
            to_email=booking.user.email,
            subject=f"Reminder: {booking.trek.trek_name} starts tomorrow",
            body=message,
        )

    return f"Sent {len(bookings)} reminders"

def get_monthly_report_data():
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()

    current_month_start = today.replace(day=1)
    previous_month_end = current_month_start - timedelta(days=1)
    previous_month_start = previous_month_end.replace(day=1)

    treks = Trek.query.filter(
        Trek.trek_status == "completed",
        Trek.end_date >= previous_month_start,
        Trek.end_date < current_month_start,
    ).all()

    trek_details = []
    total_participants = 0

    for trek in treks:
        bookings = Booking.query.filter(
            Booking.trek_id == trek.id,
            Booking.status.in_(("confirmed", "completed")),
        ).all()

        participants = sum(
            booking.slots_booked for booking in bookings
        )

        total_participants += participants

        trek_details.append({
            "name": trek.trek_name,
            "participants": participants,
        })

    trek_details.sort(
        key=lambda trek: trek["participants"],
        reverse=True,
    )

    return {
        "month": previous_month_start.strftime("%B %Y"),
        "total_treks": len(treks),
        "total_participants": total_participants,
        "popular_treks": trek_details[:5],
    }

@shared_task
def send_monthly_report():
    report = get_monthly_report_data()

    html_body = render_template(
        "monthly_report.html",
        report=report,
    )

    plain_body = (
        f"Trekking report for {report['month']}\n"
        f"Treks conducted: {report['total_treks']}\n"
        f"Participant places: {report['total_participants']}"
    )

    admins = User.query.filter_by(
        role="admin",
        approval_status="approved",
    ).all()

    for admin in admins:
        send_email(
            to_email=admin.email,
            subject=f"Monthly Trekking Report — {report['month']}",
            body=plain_body,
            html_body=html_body,
        )

    return f"Sent monthly report to {len(admins)} admins"

@shared_task
def export_trekking_history(user_id):
    user = db.session.get(User, user_id)

    if (
        not user
        or user.role != "user"
        or user.approval_status != "approved"
    ):
        return "User is not eligible for export"

    bookings = (
        Booking.query
        .join(Trek, Booking.trek_id == Trek.id)
        .filter(
            Booking.user_id == user.id,
            or_(Booking.status == "cancelled", Trek.trek_status == "completed"),
        )
        .order_by(Trek.start_date.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Trek",
        "Location",
        "Start Date",
        "End Date",
        "Slots Booked",
        "Booking Date",
        "Booking Status",
        "Trek Status",
        "Payment Status",
    ])

    for booking in bookings:
        trek = booking.trek

        writer.writerow([
            safe_csv_text(trek.trek_name),
            safe_csv_text(trek.location),
            trek.start_date.isoformat(),
            trek.end_date.isoformat(),
            booking.slots_booked,
            booking.booking_date.isoformat(),
            booking.status,
            trek.trek_status,
            booking.payment_status,
        ])

    csv_bytes = output.getvalue().encode("utf-8-sig")
    output.close()

    send_email(
        to_email=user.email,
        subject="Your trekking history export is ready",
        body=(
            f"Hello {user.username},\n\n"
            "Your trekking history export is complete. "
            "The CSV file is attached."
        ),
        attachment=csv_bytes,
        filename="trekking_history.csv",
    )

    return f"Exported {len(bookings)} bookings"

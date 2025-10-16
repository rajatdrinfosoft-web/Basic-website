from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def home():
    # Popular tour in india
    cards = [
        {
            "image": "https://www.pilgrimpackages.com/upload/package/image-D33QMAIRU7N7HFIV.jpg",
            "title": "Amarnath Yatra by Helicopter",
            "description": "A 6-day 5-Nights spiritual journey to the sacred Amarnath cave",
            "rating": "⭐⭐⭐⭐⭐",
            "price": "₹15,999",
            "link": "#"
        },
        {
            "image": "https://www.pilgrimpackages.com/upload/package/image-Q178D7067V0TP584.jpg",
            "title": "Char Dham Yatra 2025",
            "description": "Experience the holy Char Dham circuit — Yamunotri, Gangotri, Kedarnath, and Badrinath",
            "rating": "⭐⭐⭐⭐",
            "price": "₹25,999",
            "link": "#"
        },
        {
            "image": "https://www.pilgrimpackages.com/upload/package/image-MS3XW2M4WJJB33C2.jpg",
            "title": "Golden Temple Tour",
            "description": "A 3-day visit to the iconic Golden Temple in Amritsar, a spiritual center for Sikhs worldwide.",
            "rating": "⭐⭐⭐⭐",
            "price": "₹5,999",
            "link": "#"
        }
    ]
    # Carousel event cards
    events = [
        {
            "image": "https://www.pilgrimpackages.com/upload/package/image-Q178D7067V0TP584.jpg",
            "title": "Amarnath Yatra Opening 2025",
            "date": "June 20, 2025",
            "destination": "Amarnath Cave, J&K",
            "link":"#"
        },
        {
            "image": "https://www.pilgrimpackages.com/upload/package/image-D33QMAIRU7N7HFIV.jpg",
            "title": "Kedarnath Opening Ceremony",
            "date": "May 15, 2025",
            "destination": "Kedarnath, Uttarakhand",
            "link":"#"
        },
        {
            "image": "https://www.pilgrimpackages.com/upload/package/image-D0AJWIWGNTX4K1KC.jpg",
            "title": "Char Dham Closing",
            "date": "Oct 25, 2025",
            "destination": "Uttarakhand",
            "link":"#"
        }
    ]

    return render_template('home.html', cards=cards, events=events)     



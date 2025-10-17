from app import create_app, db
from app.models import Package, Event, User

app = create_app()

with app.app_context():
    # Create admin user (only if not exists)
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)

    # Seed packages from extra data
    packages = [
        {
            'title': 'Char Dham Yatra',
            'description': 'Experience the spiritual journey to the four sacred shrines of Yamunotri, Gangotri, Kedarnath, and Badrinath in Uttarakhand.',
            'price': '₹15,999',
            'rating': '⭐⭐⭐⭐⭐',
            'image': 'https://www.pilgrimpackages.com/upload/package/image-D33QMAIRU7N7HFIV.jpg',
            'duration': '10 Days / 09 Nights',
            'destination': 'Uttarakhand',
            'best_time': 'May - October',
            'group_size': '2-40 persons',
            'overview': 'Experience the spiritual journey to the four sacred shrines of Yamunotri, Gangotri, Kedarnath, and Badrinath in Uttarakhand. Our Char Dham Yatra package includes comfortable transport, meals, hotel stays, and guided sightseeing.',
            'itinerary': 'Day 1: Arrival in Haridwar, transfer to Barkot\nDay 2: Yamunotri Temple visit\nDay 3: Barkot to Uttarkashi\nDay 4: Gangotri Temple visit\nDay 5: Uttarkashi to Guptkashi\nDay 6: Kedarnath Temple visit\nDay 7: Guptkashi to Badrinath\nDay 8: Badrinath Temple visit\nDay 9: Return to Haridwar\nDay 10: Departure',
            'inclusions': 'Accommodation in quality hotels\nDaily meals (breakfast & dinner)\nAll transfers and sightseeing by AC vehicle\nExperienced tour guide\nAssistance for temple darshan',
            'exclusions': 'Personal expenses\nEntry fees at temples/monuments\nAny items not mentioned in inclusions'
        },
        {
            'title': 'Amarnath Yatra by Helicopter',
            'description': 'A 6-day 5-Nights spiritual journey to the sacred Amarnath cave',
            'price': '₹15,999',
            'rating': '⭐⭐⭐⭐⭐',
            'image': 'https://www.pilgrimpackages.com/upload/package/image-D33QMAIRU7N7HFIV.jpg',
            'duration': '6 Days / 5 Nights',
            'destination': 'Jammu & Kashmir',
            'best_time': 'July - August',
            'group_size': '2-20 persons',
            'overview': 'Embark on a spiritual journey to the sacred Amarnath cave via helicopter. Experience the divine ambiance and witness the natural ice lingam.',
            'itinerary': 'Day 1: Arrival in Srinagar\nDay 2: Helicopter to Amarnath\nDay 3: Darshan and return\nDay 4: Srinagar sightseeing\nDay 5: Free day\nDay 6: Departure',
            'inclusions': 'Helicopter transfers\nAccommodation\nMeals\nGuide services',
            'exclusions': 'Personal expenses\nEntry fees'
        },
        {
            'title': 'Golden Temple Tour',
            'description': 'A 3-day visit to the iconic Golden Temple in Amritsar, a spiritual center for Sikhs worldwide.',
            'price': '₹5,999',
            'rating': '⭐⭐⭐⭐⭐',
            'image': 'https://www.pilgrimpackages.com/upload/package/image-MS3XW2M4WJJB33C2.jpg',
            'duration': '3 Days / 2 Nights',
            'destination': 'Punjab',
            'best_time': 'October - March',
            'group_size': '2-30 persons',
            'overview': 'Visit the magnificent Golden Temple, the holiest shrine of Sikhism, and experience the divine serenity.',
            'itinerary': 'Day 1: Arrival in Amritsar\nDay 2: Golden Temple visit\nDay 3: Departure',
            'inclusions': 'Hotel accommodation\nMeals\nLocal transport\nGuide',
            'exclusions': 'Personal expenses\nEntry fees'
        }
    ]

    for pkg_data in packages:
        package = Package(**pkg_data)
        db.session.add(package)

    # Seed events
    events = [
        {
            'title': 'Amarnath Yatra Opening 2025',
            'date': 'June 20, 2025',
            'destination': 'Amarnath Cave, J&K',
            'image': 'https://www.pilgrimpackages.com/upload/package/image-Q178D7067V0TP584.jpg',
            'link': '#'
        },
        {
            'title': 'Kedarnath Opening Ceremony',
            'date': 'May 15, 2025',
            'destination': 'Kedarnath, Uttarakhand',
            'image': 'https://www.pilgrimpackages.com/upload/package/image-D33QMAIRU7N7HFIV.jpg',
            'link': '#'
        },
        {
            'title': 'Char Dham Closing',
            'date': 'Oct 25, 2025',
            'destination': 'Uttarakhand',
            'image': 'https://www.pilgrimpackages.com/upload/package/image-D0AJWIWGNTX4K1KC.jpg',
            'link': '#'
        }
    ]

    for event_data in events:
        event = Event(**event_data)
        db.session.add(event)

    db.session.commit()
    print("Database seeded successfully!")

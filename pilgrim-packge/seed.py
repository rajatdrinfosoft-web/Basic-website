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
            'gallery_images': 'https://www.pilgrimpackages.com/upload/package/image-D33QMAIRU7N7HFIV.jpg,https://www.pilgrimpackages.com/upload/package/image-D0AJWIWGNTX4K1KC.jpg,https://www.pilgrimpackages.com/upload/package/image-Q178D7067V0TP584.jpg',
            'duration': '10 Days / 09 Nights',
            'destination': 'Uttarakhand',
            'best_time': 'May - October',
            'group_size': '2-40 persons',
            'overview': 'Experience the spiritual journey to the four sacred shrines of Yamunotri, Gangotri, Kedarnath, and Badrinath in Uttarakhand. Our Char Dham Yatra package includes comfortable transport, meals, hotel stays, and guided sightseeing.',
            'itinerary': 'Day 1: Arrival in Haridwar, transfer to Barkot\nDay 2: Yamunotri Temple visit\nDay 3: Barkot to Uttarkashi\nDay 4: Gangotri Temple visit\nDay 5: Uttarkashi to Guptkashi\nDay 6: Kedarnath Temple visit\nDay 7: Guptkashi to Badrinath\nDay 8: Badrinath Temple visit\nDay 9: Return to Haridwar\nDay 10: Departure',
            'itinerary_days': 'Day 1: Arrival in Haridwar - Transfer to Barkot (210kms/7hrs)\nDay 2: Yamunotri Temple Darshan - Return to Barkot\nDay 3: Barkot to Uttarkashi (100kms/4hrs)\nDay 4: Gangotri Temple Darshan - Return to Uttarkashi\nDay 5: Uttarkashi to Guptkashi (220kms/8hrs)\nDay 6: Kedarnath Temple Darshan - Return to Guptkashi\nDay 7: Guptkashi to Badrinath (200kms/7hrs)\nDay 8: Badrinath Temple Darshan - Local sightseeing\nDay 9: Badrinath to Rudraprayag - Transfer to Haridwar\nDay 10: Haridwar to Delhi - Departure',
            'inclusions': 'Accommodation in quality hotels\nDaily meals (breakfast & dinner)\nAll transfers and sightseeing by AC vehicle\nExperienced tour guide\nAssistance for temple darshan',
            'exclusions': 'Personal expenses\nEntry fees at temples/monuments\nAny items not mentioned in inclusions',
            'highlights': 'Visit all four sacred shrines of Char Dham\nExperience divine blessings at Yamunotri, Gangotri, Kedarnath, and Badrinath\nComfortable accommodation and transportation\nExperienced spiritual guides\nSacred rituals and ceremonies',
            'accommodation_details': 'Quality hotels with basic amenities\nTwin sharing rooms\n24/7 hot water\nClean and hygienic environment\nNear temple premises where possible',
            'transportation_details': 'AC vehicles for all transfers\nExperienced drivers\nComfortable seating\nTimely departures and arrivals\nEmergency vehicle support',
            'cancellation_policy': '30 days before: 25% cancellation charges\n15-30 days before: 50% cancellation charges\n7-15 days before: 75% cancellation charges\nLess than 7 days: 100% cancellation charges',
            'terms_conditions': 'ID proof required at check-in\nAdvance payment mandatory\nWeather conditions may affect itinerary\nManagement reserves right to change itinerary\nMedical certificate required for senior citizens',
            'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
            'map_location': '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3444.156!2d78.0322!3d30.3165!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x390929c356c888af%3A0x4c3562c032518799!2sGangotri%2C%20Uttarakhand!5e0!3m2!1sen!2sin!4v1634567890123!5m2!1sen!2sin" width="100%" height="300" style="border:0;" allowfullscreen="" loading="lazy"></iframe>'
        },
        {
            'title': 'Amarnath Yatra by Helicopter',
            'description': 'A 6-day 5-Nights spiritual journey to the sacred Amarnath cave',
            'price': '₹15,999',
            'rating': '⭐⭐⭐⭐⭐',
            'image': 'https://www.pilgrimpackages.com/upload/package/image-D33QMAIRU7N7HFIV.jpg',
            'gallery_images': 'https://www.pilgrimpackages.com/upload/package/image-D33QMAIRU7N7HFIV.jpg,https://www.pilgrimpackages.com/upload/package/image-Q178D7067V0TP584.jpg',
            'duration': '6 Days / 5 Nights',
            'destination': 'Jammu & Kashmir',
            'best_time': 'July - August',
            'group_size': '2-20 persons',
            'overview': 'Embark on a spiritual journey to the sacred Amarnath cave via helicopter. Experience the divine ambiance and witness the natural ice lingam.',
            'itinerary': 'Day 1: Arrival in Srinagar\nDay 2: Helicopter to Amarnath\nDay 3: Darshan and return\nDay 4: Srinagar sightseeing\nDay 5: Free day\nDay 6: Departure',
            'itinerary_days': 'Day 1: Arrival at Srinagar Airport - Transfer to hotel\nDay 2: Early morning helicopter transfer to Amarnath - Holy darshan - Return to Srinagar\nDay 3: Full day for Amarnath darshan if required - Evening free\nDay 4: Srinagar city sightseeing - Mughal Gardens, Dal Lake\nDay 5: Free day for shopping and relaxation\nDay 6: Transfer to airport - Departure',
            'inclusions': 'Helicopter transfers\nAccommodation\nMeals\nGuide services',
            'exclusions': 'Personal expenses\nEntry fees',
            'highlights': 'Helicopter journey to Amarnath\nWitness the sacred ice lingam\nStay in Srinagar with lake views\nVisit Mughal Gardens\nSpiritual guide assistance',
            'accommodation_details': 'Luxury houseboats on Dal Lake\nDeluxe hotel rooms\nAll modern amenities\nScenic views\nTraditional Kashmiri hospitality',
            'transportation_details': 'Helicopter transfers to Amarnath\nAC vehicles for local transport\nAirport transfers\nExperienced drivers\nSafety equipment',
            'cancellation_policy': '30 days before: 50% cancellation charges\n15-30 days before: 75% cancellation charges\nLess than 15 days: 100% cancellation charges',
            'terms_conditions': 'Helicopter operations subject to weather\nMedical fitness certificate required\nID proof mandatory\nAdvance booking required\nWeather may affect schedule',
            'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
            'map_location': '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3444.156!2d74.8765!3d34.0837!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x38e1850686059d6f%3A0x3c6f4c3c3c3c3c3c!2sAmarnath%20Cave!5e0!3m2!1sen!2sin!4v1634567890123!5m2!1sen!2sin" width="100%" height="300" style="border:0;" allowfullscreen="" loading="lazy"></iframe>'
        },
        {
            'title': 'Golden Temple Tour',
            'description': 'A 3-day visit to the iconic Golden Temple in Amritsar, a spiritual center for Sikhs worldwide.',
            'price': '₹5,999',
            'rating': '⭐⭐⭐⭐⭐',
            'image': 'https://www.pilgrimpackages.com/upload/package/image-MS3XW2M4WJJB33C2.jpg',
            'gallery_images': 'https://www.pilgrimpackages.com/upload/package/image-MS3XW2M4WJJB33C2.jpg',
            'duration': '3 Days / 2 Nights',
            'destination': 'Punjab',
            'best_time': 'October - March',
            'group_size': '2-30 persons',
            'overview': 'Visit the magnificent Golden Temple, the holiest shrine of Sikhism, and experience the divine serenity.',
            'itinerary': 'Day 1: Arrival in Amritsar\nDay 2: Golden Temple visit\nDay 3: Departure',
            'itinerary_days': 'Day 1: Arrival at Amritsar Railway Station/Airport - Transfer to hotel - Evening visit to Golden Temple\nDay 2: Morning prayers at Golden Temple - Visit Jallianwala Bagh and Partition Museum - Evening free\nDay 3: Morning breakfast - Transfer to station/airport - Departure',
            'inclusions': 'Hotel accommodation\nMeals\nLocal transport\nGuide',
            'exclusions': 'Personal expenses\nEntry fees',
            'highlights': 'Visit the Golden Temple\nExperience langar (free community meal)\nHistorical sites of Jallianwala Bagh\nPartition Museum visit\nSikh cultural experience',
            'accommodation_details': 'Comfortable hotels near Golden Temple\nClean and well-maintained rooms\nWiFi and modern amenities\n24/7 room service\nCultural ambiance',
            'transportation_details': 'AC vehicle for sightseeing\nAirport/railway station transfers\nExperienced local drivers\nComfortable and safe travel\nGPS tracking enabled',
            'cancellation_policy': '7 days before: 25% cancellation charges\n3-7 days before: 50% cancellation charges\nLess than 3 days: 75% cancellation charges\nSame day: 100% cancellation charges',
            'terms_conditions': 'Dress code for temple visit\nRespect religious sentiments\nPhotography restrictions in temple\nID proof required\nAdvance booking recommended',
            'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
            'map_location': '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3444.156!2d74.8765!3d31.6200!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x391964aa569e7355%3A0x71fa75e5e4c0a2a1!2sGolden%20Temple!5e0!3m2!1sen!2sin!4v1634567890123!5m2!1sen!2sin" width="100%" height="300" style="border:0;" allowfullscreen="" loading="lazy"></iframe>'
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

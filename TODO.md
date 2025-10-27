# TODO: Load Sample Data for Pilgrim Packages Web App

## Overview
Modify `seed.py` to fetch real pilgrim package data from online sources, download images from various websites, and populate the database slowly one by one with error handling.

## Steps
- [x] Add necessary imports to `seed.py` (requests, time, os, uuid, etc.)
- [x] Define function to fetch package data from online sources (e.g., scrape or use APIs)
- [x] Define function to download and save images locally
- [x] Update the packages seeding logic to fetch data dynamically, one package at a time
- [x] Add error handling and delays between requests to avoid getting stuck
- [x] Update events seeding if needed
- [ ] Test the seeding script
- [ ] Run the seed script to populate the database

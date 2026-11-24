import re
from decimal import Decimal, InvalidOperation
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
import requests
# Update 'your_app' to match your Django app name
from brownsville.models import Agent, ListingPhoto, Listing
from time import sleep

def clean_decimal(val: str | None) -> Decimal | None:
    if not val:
        return None
    cleaned = re.sub(r"[^\d.]", "", val)
    try:
        return Decimal(cleaned) if cleaned else None
    except InvalidOperation:
        return None


def clean_int(val: str | None) -> int | None:
    if not val:
        return None
    cleaned = re.sub(r"[^\d]", "", val)
    return int(cleaned) if cleaned else None


class Command(BaseCommand):
    help = "Scrapes all MLS listings from Texas Stars Realty Group, LLC"

    def handle(self, *args, **options):
        more = True
        page = 1
        links = []
        while more:
            r = requests.get(f"https://www.usamls.net/harlingen/default.asp?content=office_listings&menu_id=63751&this_format=0&sortby=2&sort_dir=asc&listing_off_id=534&page={page}")
            for x in range(1,10):
                try:
                    link = 'https://www.usamls.net/harlingen/default.asp?content=expanded' + r.text.split('<a href="default.asp?content=expanded')[x].split('" target=')[0]
                    links += [link]
                except:
                    more = False
                    break
            page += 1
        for link in links:
            sleep(1)
            r = requests.get(link)
            base_url = "https://www.usamls.net/riograndemls/"
            try:
                html = r.text
            except FileNotFoundError:
                raise CommandError(f"File not found: {html_path}")

            soup = BeautifulSoup(html, "html.parser")

            # 1. Extract all "Heading: Value" pairs from the Listing Details section
            details: dict[str, str | None] = {}
            for row in soup.select(".expanded_field_display"):
                heading_el = row.select_one(".expanded_field_heading")
                value_el = row.select_one(".expanded_field_value")
                if heading_el and value_el:
                    key = heading_el.get_text(strip=True).rstrip(":")
                    link = value_el.find("a")
                    val = (
                        link["href"].strip()
                        if link and link.get("href")
                        else value_el.get_text(strip=True)
                    )
                    val = val.replace("\xa0", "").strip()
                    details[key] = val or None

            mls_number = details.get("MLS Number")
            if not mls_number:
                raise CommandError("Could not find MLS Number in HTML.")

            # 2. Look up existing Agent by listing_agt_id (never writes to Agent table)
            agent = None
            agent_link = soup.select_one(".website_agent_photo_padding a")
            if agent_link and agent_link.get("href"):
                parsed_href = urlparse(agent_link["href"])
                agent_mls_id = parse_qs(parsed_href.query).get("listing_agt_id", [None])[0]
                if agent_mls_id:
                    agent = Agent.objects.filter(mls_id=agent_mls_id).first()

            listing, created = Listing.objects.update_or_create(
                mls_number=mls_number,
                defaults={
                    "agent": agent,
                    "list_price": clean_decimal(details.get("List Price")),
                    "present_use": details.get("Present Use"),
                    "suitable_use": details.get("Suitable Use"),
                    "property_type": details.get("Property Type"),
                    "street_number": details.get("Street #"),
                    "street_name": details.get("Street Name"),
                    "street_type": details.get("Street Type"),
                    "subdivision": details.get("Subdivision"),
                    "city": details.get("City"),
                    "area": details.get("Area"),
                    "year_built": clean_int(details.get("Year Built")),
                    "estimated_living_sqft": clean_int(details.get("Estimated Living SqFt")),
                    "apx_lot_sqft": clean_int(details.get("Apx Lot SqFt")),
                    "bedrooms": clean_int(details.get("Bedrooms")),
                    "baths": clean_decimal(details.get("Baths")),
                    "half_baths": clean_int(details.get("1/2 Baths")),
                    "stories": details.get("# Stories"),
                    "parking_spaces": clean_int(details.get("# Parking Spaces")),
                    "apx_acreage": clean_decimal(details.get("Apx Acreage")),
                    "access": details.get("Access"),
                    "topography": details.get("Topography"),
                    "grounds": details.get("Grounds"),
                    "parking": details.get("Parking"),
                    "site_features": details.get("Site Features"),
                    "water": details.get("Water"),
                    "sewer": details.get("Sewer"),
                    "school_district": details.get("School District"),
                    "elementary_school": details.get("Elementary School"),
                    "middle_school": details.get("Middle School"),
                    "high_school": details.get("High School"),
                    "virtual_tour_video": details.get("Virtual Tour/Video"),
                },
            )

            # 4. Extract and save ListingPhotos
            photo_urls: list[str] = []
            js_match = re.search(
                r"lstImage\s*=\s*new\s+additional_photo_array2\((.*?)\);",
                html,
                re.DOTALL,
            )
            if js_match:
                raw_paths = re.findall(r"['\"]([^'\"]+)['\"]", js_match.group(1))
                photo_urls = [urljoin(base_url, p) for p in raw_paths]
            else:
                main_img = soup.select_one("#main_photo")
                if main_img and main_img.get("src"):
                    photo_urls.append(urljoin(base_url, main_img["src"]))

            ListingPhoto.objects.bulk_create(
                [ListingPhoto(listing=listing, path=url) for url in photo_urls]
            )

            action = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{action}: {listing} | Agent: {listing.agent} | Photos: {len(photo_urls)}"
                )
            )
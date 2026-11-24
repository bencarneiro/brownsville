from django.db import models
from urllib.parse import quote_plus

class Agent(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    photo = models.CharField(max_length=100, blank=True, null=True)
    mls_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name} ({self.mls_id})"

class Listing(models.Model):
    agent = models.ForeignKey(
        "Agent",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    mls_number = models.CharField(max_length=50, unique=True)
    list_price = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    present_use = models.CharField(max_length=100, blank=True, null=True)
    suitable_use = models.CharField(max_length=100, blank=True, null=True)
    property_type = models.CharField(max_length=100, blank=True, null=True)
    street_number = models.CharField(max_length=50, blank=True, null=True)
    street_name = models.CharField(max_length=255, blank=True, null=True)
    street_type = models.CharField(max_length=100, blank=True, null=True)
    subdivision = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)
    year_built = models.PositiveSmallIntegerField(blank=True, null=True)
    estimated_living_sqft = models.PositiveIntegerField(blank=True, null=True)
    apx_lot_sqft = models.PositiveIntegerField(blank=True, null=True)
    bedrooms = models.PositiveSmallIntegerField(blank=True, null=True)
    baths = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    half_baths = models.PositiveSmallIntegerField(blank=True, null=True)
    stories = models.CharField(max_length=50, blank=True, null=True)
    parking_spaces = models.PositiveIntegerField(blank=True, null=True)
    apx_acreage = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    access = models.CharField(max_length=100, blank=True, null=True)
    topography = models.CharField(max_length=100, blank=True, null=True)
    grounds = models.CharField(max_length=255, blank=True, null=True)
    parking = models.CharField(max_length=255, blank=True, null=True)
    site_features = models.TextField(blank=True, null=True)
    water = models.CharField(max_length=100, blank=True, null=True)
    sewer = models.CharField(max_length=100, blank=True, null=True)
    school_district = models.CharField(max_length=150, blank=True, null=True)
    elementary_school = models.CharField(max_length=150, blank=True, null=True)
    middle_school = models.CharField(max_length=150, blank=True, null=True)
    high_school = models.CharField(max_length=150, blank=True, null=True)
    virtual_tour_video = models.URLField(max_length=500, blank=True, null=True)
    priority = models.PositiveIntegerField(null=True, blank=True)
    
    @property
    def highlight_photo(self):
        return (
            self.listingphoto_set.filter(is_highlight=True).first()
            or self.listingphoto_set.first()
        )

    @property
    def google_maps_url(self) -> str:
        street = " ".join(filter(None, [self.street_number, self.street_name, self.street_type]))
        address = ", ".join(filter(None, [street, self.city, "TX"]))
        return f"https://www.google.com/maps/search/?api=1&query={quote_plus(address)}"

    def __str__(self):
        return f"MLS #{self.mls_number} - {self.street_number} {self.street_name}, {self.city}"

class ListingPhoto(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE
    )
    path = models.CharField(max_length=500)
    slug = models.CharField(max_length=100, null=True, blank=True)
    is_highlight = models.BooleanField(default=False, null=False, blank=True)

    def __str__(self):
        return f"Photo for MLS #{self.listing.mls_number}: {self.path}"
from django.shortcuts import render, get_object_or_404
from brownsville.models import Listing
from django.db.models import Q
# Create your views here.
def home(request):
    residential = Listing.objects.exclude(
    Q(property_type__icontains="commercial") | Q(property_type__icontains="acreage")
).order_by("-priority")
    commercial = Listing.objects.filter(
    Q(property_type__icontains="commercial") | Q(property_type__icontains="acreage")
).order_by("-priority")

    return render(request, "home.html", { "residential": residential,"commercial": commercial})

def listing(request, id):
    try:
        listing = Listing.objects.get(mls_number=id)
    except:
        return redirect("")
    return render(request, "listing.html", {"listing": listing})
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import DealerReview
# from .restapis import related methods
from .restapis import get_dealers_from_cf
from .restapis import get_dealer_reviews_from_cf
from .restapis import post_request

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def static_page(request):
    return render(request, 'djangoapp/static_page.html')

# Create an `about` view to render a static about page
def about_page(request):
    return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact_page(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...

def login_request(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have successfully logged in.')
            return redirect('admin')  # Replace 'home' with the URL name of your home page
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, 'djangoapp/login.html')

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...

def logout_request(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('admin')

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...

def registration_request(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created. You can now log in.')
            return redirect('login')  # Replace 'login' with the URL name of your login page
    else:
        form = UserCreationForm()
    return render(request, 'djangoapp/signup.html', {'form': form})

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = 'https://us-south.functions.appdomain.cloud/api/v1/web/97ac4e72-d24d-42cf-a85d-abc24849c4ca/dealership-package/get-dealership'
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after successful registration
            messages.success(request, 'Your account has been created. You are now logged in.')
            return redirect('admin')  # Redirect to the home page after successful registration and login
    else:
        form = UserCreationForm()
    return render(request, 'djangoapp/registration.html', {'form': form})


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id, api_key):
    dealer = get_dealer_by_id(dealer_id, api_key)
    reviews = get_dealer_reviews_from_cf('https://us-south.functions.appdomain.cloud/api/v1/web/97ac4e72-d24d-42cf-a85d-abc24849c4ca/dealership-package/get-review', dealer_id, api_key)

    # Iterate through the reviews and print sentiment
    for review in reviews:
        print(f"Review ID: {review.id}")
        print(f"Sentiment: {review.sentiment}")
        print(f"Reviewer Name: {review.name}")
        print(f"Review Text: {review.review}")
        print(f"Purchase: {review.purchase}")
        print(f"Purchase Date: {review.purchase_date}")
        print(f"Car Make: {review.car_make}")
        print(f"Car Model: {review.car_model}")
        print(f"Car Year: {review.car_year}")
        print()

    context = {
        "dealer": dealer,
        "reviews": reviews,
    }
    return render(request, "dealer_details.html", context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    # Prepare review data
    review = {
        "time": datetime.utcnow().isoformat(),
        "name": request.user.username,
        "dealership": dealer_id,
        "review": "This is a great car dealer",  # Replace with the actual review text
        # Add other review attributes as needed
    }

    # Create JSON payload
    json_payload = {
        "review": review
    }

    # Define the URL for the review-post cloud function
    POST_API_URL = "https://us-south.functions.appdomain.cloud/api/v1/web/97ac4e72-d24d-42cf-a85d-abc24849c4ca/dealership-package/post-review"  # Replace with the actual URL

    # Send POST request
    response = post_request(POST_API_URL, json_payload, dealerId=dealer_id)

    # Check the response and return appropriate result
    if response and response.status_code == 200:
        # Review was successfully added
        return HttpResponse("Review added successfully", status=200)
    else:
        # There was an error adding the review
        return HttpResponse("Failed to add review", status=500)


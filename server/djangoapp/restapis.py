
import requests
import json
# import related models here
from .models import CarDealer
from requests.auth import HTTPBasicAuth
from .models import DealerReview


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, api_key=None, params=None, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    response = None  # Initialize the response variable
    try:
        headers = {'Content-Type': 'application/json'}
        if api_key:
            auth = HTTPBasicAuth('apikey', api_key)
            response = requests.get(url, headers=headers, params=params, auth=auth, **kwargs)
        else:
            response = requests.get(url, headers=headers, params=params, **kwargs)
        response.raise_for_status()  # Raise exception for 4xx and 5xx status codes
        json_data = response.json()  # Parse JSON response
        return json_data  # Return parsed JSON data
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return None  # Return None in case of error

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    response = None  # Initialize the response variable
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, json=json_payload, params=kwargs)
        response.raise_for_status()  # Raise exception for 4xx and 5xx status codes
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return response


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealer_id, api_key):
    results = []
    json_result = get_request(url, dealerId=dealer_id, api_key=api_key)
    if json_result:
        reviews = json_result.get("reviews", [])
        for review in reviews:
            reviewer_name = review.get("reviewer_name", "")
            review_text = review.get("review_text", "")
            # ... extract other attributes as before ...

            # Analyze sentiment of the review text
            sentiment = analyze_review_sentiments(review_text, api_key)

            # Create a DealerReview object with extracted values and sentiment
            review_obj = DealerReview(
                dealership=dealer_id,
                name=reviewer_name,
                review=review_text,
                purchase=purchase,
                purchase_date=purchase_date,
                car_make=car_make,
                car_model=car_model,
                car_year=car_year,
                sentiment=sentiment,  # Assign sentiment to the review object
                id=review_id
            )
            results.append(review_obj)
    return results



# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text, api_key, version='2021-09-01', features='sentiment', return_analyzed_text=True):
    url = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/YOUR_INSTANCE_ID/v1/analyze'
    params = {
        'version': version,
        'features': features,
        'return_analyzed_text': return_analyzed_text,
        'text': text
    }
    response = get_request(url, api_key, **params)
    if response and response.status_code == 200:
        data = response.json()
        sentiment = data.get('sentiment', {}).get('document', {}).get('label', 'Unknown')
        return sentiment
    else:
        print("Failed to analyze sentiment.")
        return 'Unknown'





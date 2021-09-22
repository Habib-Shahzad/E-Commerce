from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment, Watchlist
import datetime

def index(request):
    active_listings = Listing.objects.all().exclude(running=False)
    return render(request, "auctions/index.html",{
        "listings": active_listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def createlisting(request):
    return render(request, "auctions/createlisting.html")


def create(request):
    current_user = request.user
    user = User.objects.get(username=current_user)
    try:
        now = datetime.datetime.now()
        time = "Created " + str(now.strftime('%B')) + "." + str(now.day) + ". " + str(now.year) + " " + str(now.strftime('%I:%M:%p'))
        if request.method=="POST":
            title=request.POST['title']
            bid=request.POST['bid']
            if request.POST['category']:category=request.POST['category']
            else: category=None
            description=request.POST['description']
            if request.POST['image']: image=request.POST['image']
            else: image=None
            listing = Listing(title=title, price=bid, category=category, description=description, image=image, user=user)
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    except ValueError:
        return render(request, "auctions/createlisting.html", {
            'error': True
        })


    
def count_bids(listing):
    bids = Bid.objects.filter(listing__exact = listing)
    if bids: return bids.count()
    else: return 0

def item(request,name):
    if request.user.is_active:
        current_user = request.user
        user = User.objects.get(username=current_user)
        listing = Listing.objects.get(pk=name)
        highest, person = max_biduser(listing)
        ended = not listing.running
        listing.user = listing.user
        if listing.user==user: owner=True
        else: owner=False
        watchList = Watchlist.objects.filter(user=user, listing=listing)
        count = watchList.count()
        if count==0: already=False
        else: already=True
        all_comments = Comment.objects.filter(listing__exact=listing)
        return render(request, "auctions/item.html",{
            'listing':listing,
            'count': count_bids(listing),
            'comments': all_comments,
            'owner': owner,
            'ended': ended,
            'highest': highest,
            'person': person,
            'already': already
        })
    else:
        return HttpResponseRedirect(reverse("login"))


def max_bid(listing):
    all_bids = []
    bids = Bid.objects.filter(listing__exact = listing)
    for any_bid in bids:
        all_bids.append(any_bid.bid)  
    if all_bids: return max(all_bids)
    else: return listing.price

def max_biduser(listing):
    all_bids = []
    bids = Bid.objects.filter(listing__exact = listing)
    for any_bid in bids:
        all_bids.append(any_bid.bid)  
    if all_bids:
        highest = max(all_bids)
        person = Bid.objects.get(bid=highest, listing=listing)
        return highest, person
    else: return listing.price, listing.user


def bid(request,name):
    listing = Listing.objects.get(pk=name)
    ended = not listing.running
    all_comments = Comment.objects.filter(listing__exact=listing)
    try:
        bid = int(request.POST['bid'])
        current_user = request.user
        user = User.objects.get(username=current_user)
        if listing.user==user: owner=True
        else: owner=False
        starting_bid = listing.price
        highest_bid = max_bid(listing)
        if bid<starting_bid or bid<highest_bid:
            return render(request, "auctions/item.html", {
                    'less_bid': True,
                    'highest': highest_bid,
                    'listing': listing,
                    'count':count_bids(listing),
                    'comments': all_comments,
                    'owner':owner,
                    'ended': ended
                })

        current_bid = Bid(user=user, bid=bid, listing=listing)
        current_bid.save()
        return render(request, "auctions/item.html", {
                        'less_bid': False,
                        'listing': listing,
                        'count': count_bids(listing),
                        'comments': all_comments,
                        'ended': ended
                    })

    except:
        user = User.objects.get(username=request.user)
        if listing.user==user: owner=True
        else: owner=False
        return render(request, "auctions/item.html", {
            'empty': True,
            'listing': listing,
            'count': count_bids(listing),
            'comments': all_comments,
            'owner':owner
        })    


def listwatch(request,name):
    current_user = request.user
    user = User.objects.get(username=current_user)
    listing = Listing.objects.get(pk=name)
    ended = not listing.running
    all_comments = Comment.objects.filter(listing__exact=listing)
    watchList = Watchlist.objects.filter(user=user, listing=listing)
    count = watchList.count()
    highest, person = max_biduser(listing)
    if listing.user==user: owner=True
    else: owner=False
    if count==0:
        if listing:
            watchlist = Watchlist(user=user, listing=listing)
            watchlist.save()
        return render(request, "auctions/item.html",{
        'listing': listing,
        'already': True,
        'count': count_bids(listing),
        'owner':owner,
        'comments': all_comments,
        'added': True,
        'ended': ended,
        'highest': highest,
        'person': person
        })
    else:
        return render(request, "auctions/item.html",{
        'listing': listing,
        'already': True,
        'owner':owner,
        'count': count_bids(listing),
        'comments': all_comments,
        'ended': ended,
        'highest': highest,
        'person': person})


def removewatch(request,name):
    current_user = request.user
    user = User.objects.get(username=current_user)
    listing = Listing.objects.get(pk=name)
    watchlist = Watchlist.objects.filter(listing__exact=listing, user__exact = user).delete()
    all_comments = Comment.objects.filter(listing__exact=listing)
    highest, person = max_biduser(listing)
    if listing.user==user: owner=True
    else: owner=False
    ended = not listing.running
    return render(request, "auctions/item.html",{
    'listing':listing,
    'count': count_bids(listing),
    'comments': all_comments,
    'owner': owner,
    'ended': ended,
    'highest': highest,
    'person': person
})



def watch(request):
    try:
        current_user = request.user
        user = User.objects.get(username=current_user)
        watching = Watchlist.objects.filter(user = user).exclude(listing=None)
        if watching:
            return render(request, "auctions/watchlist.html", {
                'watchlist': watching
            } )
        else:
            return render(request, "auctions/watchlist.html", {
                'error': True
            })
    except:
        return HttpResponseRedirect(reverse("login"))


def comment(request,name):
    listing = Listing.objects.get(pk=name)
    ended = not listing.running
    current_user = request.user
    user = User.objects.get(username=current_user)
    highest, person = max_biduser(listing)
    if listing.user==user: owner=True
    else: owner=False
    all_comments = Comment.objects.filter(listing__exact=listing)
    if request.POST['comment']:
        commentTxt = request.POST['comment']
        current_comment = Comment(user=user, comment=commentTxt, listing=listing)
        current_comment.save()
        return render(request, "auctions/item.html", {
            'listing': listing,
            'comments': all_comments,
            'count': count_bids(listing),
            'owner':owner,
            'ended': ended,
            'highest': highest,
            'person': person
        })
    else:
        return render(request, "auctions/item.html", {
            'listing': listing,
            'comments': all_comments,
            'count': count_bids(listing),
            'empt': True,
            'owner':owner,
            'ended': ended,
            'highest': highest,
            'person': person
        })


def all_categories():
    listings = Listing.objects.all()
    cats = {}
    for listing in listings:
        if listing.category not in cats: 
            cats[listing.category] = []
    for key in cats:
        for listing in listings:
            if key==listing.category:
                if listing not in cats[key]:
                    cats[key].append(listing)
    return cats

def categories(request):
    cats = all_categories()
    return render(request, "auctions/categories.html", {
        'categories': cats
    })


def viewbycategory(request, name):
    cats = all_categories()
    return render(request, "auctions/viewbycategory.html", {
    'listings': cats[name],
    'category': name
})


def endauction(request, name):
    current_user = request.user
    user = User.objects.get(username=current_user)
    listing = Listing.objects.get(pk=name)
    listing.running = False
    highest, person = max_biduser(listing)
    listing.save(update_fields=['running'])
    all_comments = Comment.objects.filter(listing__exact=listing)
    return render(request, "auctions/item.html",{
        'listing':listing,
        'count': count_bids(listing),
        'ended': True,
        'comments': all_comments,
        'highest': highest,
        'person': person
    })


def closed(request):
    closed_listings = Listing.objects.all().exclude(running=True)
    return render(request, "auctions/closed.html",{
        "listings": closed_listings
    })

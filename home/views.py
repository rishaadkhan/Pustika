import json
from django.shortcuts import get_object_or_404, render,HttpResponse,redirect
from .models import books
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . forms import sellbookform ,UserProfileForm
from .models import Order,TrackUpdate,UserProfile
import requests
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
def loginsignup(request):
    return render(request,'home/loginlink.html')
def home(request):
    allProds = []
    book = books.objects.all()
    categories = books.objects.values('category')
    ca = {item['category'] for item in categories}
    cats = list(ca) 
    for cat in cats:
        prod = books.objects.filter(category = cat)
        allProds.append([prod,range(len(prod))])
    params = {'books':book, 'cats':cats, 'allProds':allProds}
    return render(request,'home/home.html',params)

def handleSignup(request):
    
    if request.method =='POST':
        username = request.POST['username']
        email = request.POST['signupemail']
        fname = request.POST['fname']
        lname = request.POST['lname']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if len(username) > 25:
            messages.error(request, "User name must be under 25 Characters")
            return redirect('/')
        if pass1 != pass2:
            messages.error(request, "Password do not match")   
            return redirect('/') 
       
        myuser = User.objects.create_user(username=username,email=email,password=pass2)   
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(request,'Your account has been created Successfully ')
        return redirect('/')
    else:
        return HttpResponse('NOT ALLOWED')   

def handleLogin(request):
    loginusername = request.POST['loginusername']
    loginpass = request.POST['loginpass']
    user = authenticate(username=loginusername,password=loginpass)
    if user is not None:
        login(request,user)
        messages.success(request,"Successfully Logged In ")
        return redirect('/')
    else:
        messages.error(request,"Please Enter the username or password correctly!")
        return redirect('/')    

@login_required(login_url='/loginsignup')
def handleLogout(request):
    logout(request)
    messages.success(request,"Successfully logged out")
    return redirect('/')      

@login_required(login_url='/loginsignup')
def sellbook(request):
    context ={'form': sellbookform()} 
    return render(request, "home/sellbook.html", context)

@login_required(login_url='/loginsignup')
def savebook(request):
    sellername = request.user.username
    book_name =  request.POST.get('book_name')
    category =  request.POST.get('category')
    price =  request.POST.get('price')
    image =  request.FILES['image']
    pickuplocation =  request.POST.get('pickuplocation')
    slug = book_name.replace(" ", "-") + "-by-" + str(sellername)
    newbook = books.objects.create(sellername=sellername, book_name = book_name, category = category, price= price,image= image,pickuplocation = pickuplocation, slug= slug)
    try:
        newbook.save()
        messages.success(request,'Your post has been added successfully, Thank you for your great effort.')
    except:
        messages.error(request,"Sorry! unable to Process..")    
    return redirect('/')

@login_required(login_url='/loginsignup')
def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        email = request.user.email
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        # order_date = request.POST.get('date',)
        order = Order(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone)
        order.save()
        updateorder = TrackUpdate(order_id=order.order_id,update="Your Order Is Placed",daysleft=7)
        updateorder.save()
        thank = True
        id = order.order_id
        return render(request, 'home/checkout.html', {'thank':thank, 'id': id})
    return render(request, 'home/checkout.html')


@login_required(login_url='/loginsignup')
def TrackOrder(request):
    mail = request.user.email
    orders = Order.objects.filter(email=mail)
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        updates = TrackUpdate.objects.filter(order_id=order_id)
        context = {'updates':updates}
        return render(request,'home/updatepage.html',context)

    return render(request,'home/trackorder.html',{'orders':orders})

def search(request):
    searchquery = request.GET['search']
    if len(searchquery)>=50:
        #allposts = Post.objects.none()
   # if len(searchquery)<1:
       # allposts = Post.objects.none()
        messages.error(request,'Please enter more than 4 characters')
        redirect('/')
    else:    
        allpoststitle = books.objects.filter(book_name__icontains=searchquery)
        allpostscontent = books.objects.filter(category__icontains=searchquery)
        allposts = allpoststitle.union(allpostscontent)
        print(allposts)
        context = {'allposts':allposts,'search':searchquery}
        return render(request,'home/search.html',context)
    return render(request,'home/search.html')


@login_required(login_url='/loginsignup')
def my_orders(request):
    mail = request.user.email
    orders = Order.objects.filter(email=mail)
    for order in orders:
        order.items_json = json.loads(order.items_json)
    context = {
        'orders': orders,
    }
    return render(request,'home/orders.html',context)



#user dashboard or profile view
def dashboard_view(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)
        user_profile.save()
    if request.method=='POST':
        form = UserProfileForm(request.POST,instance=user_profile)
        if form.is_valid():
            form.save()
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request,'home/dashboard.html',{'form':form})


#book details
def book_details(request, slug):
    book = get_object_or_404(books, slug=slug)
    context = {
        'book': book
    }
    return render(request, 'home/book_details.html', context)


#payment
@csrf_exempt
def payment(request):
    if request.method == 'POST':
        amount = 500
        # Set the parameters for the SSLCOMMERZ API
        params = {
            'store_id': 'hadij62073c48e7d22',
            'store_passwd': 'hadij62073c48e7d22@ssl',
            'total_amount': amount,
            'currency': 'BDT',
            'tran_id': 'your_transaction_id',
            'success_url': 'http://127.0.0.1:8000/',
            'fail_url': 'http://127.0.0.1:8000/',
            'cancel_url': 'http://127.0.0.1:8000/',
            'emi_option': 0,
            'cus_name': 'your_customer_name',
            'cus_email': 'your_customer_email',
            'cus_phone': 'your_customer_phone',
            'cus_add1': 'your_customer_address',
            'cus_city': 'your_customer_city',
            'cus_country': 'Bangladesh',
            'shipping_method': 'NO',
            'product_name': 'your_product_name',
            'product_category': 'your_product_category',
            'product_profile': 'your_product_profile'
        }
        # Send a request to the SSLCOMMERZ API to initiate the payment
        response = requests.post('https://sandbox.sslcommerz.com/gwprocess/v4/api.php', data=params)
        # Parse the response and get the payment gateway URL
        response_data = response.json()
        gateway_url = response_data['GatewayPageURL']
        # Redirect the user to the payment gateway URL
        return redirect(gateway_url)
    


def our_team(request):
    return render(request,'home/our_team.html')
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, CustomLoginForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            print("User registered successfully!")
            print(f"New user: {user}")
            login(request, user)  # Automatically log the user in after registration
            return redirect('dashboard')  # Redirect to dashboard 
        else:
            print("Something went wrong")
            print(form.errors)
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        print("CHEKCING VALIDITY")
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            print(f"Attempting to authenticate with email: {email}")
            user = authenticate(request, username=email, password=password)
            if user is not None:
                print("User authenticated successfully!")
                login(request, user)
                return redirect('dashboard')
            else:
                print("Authentication failed.")
                form.add_error(None, "Invalid email or password.")
        else:
            print(form.errors)
    else:
        
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    if request.user:
        logout(request)
    return redirect('login')
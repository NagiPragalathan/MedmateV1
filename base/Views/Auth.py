# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from base.models import UserRole, PatientDocument
from django.contrib.auth import authenticate, login
import g4f

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page after successful login
        else:
            return render(request, 'Auth/login.html', {'error': 'Invalid username or password'})
    return render(request, 'Auth/login.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user_type = request.POST.get('userType')
        print(username, password)
        user = User.objects.create_user(username=username, password=password)
        user_Role = UserRole(user=user, role=user_type)
        user_Role.save()
        
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page after successful signup
        else:
            return render(request, 'Auth/signup.html', {'error': 'Signup failed'})
    return render(request, 'Auth/signup.html')


# views.py
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from g4f.client import Client



@csrf_exempt  # To bypass CSRF protection for this example, you might want to handle CSRF tokens properly in production
def apichatwithbot(request):
    if request.method == 'POST':
        try:
            # Get the JSON body from the request
            request_data = json.loads(request.body.decode('utf-8'))
            user_query = request_data.get('user_query', '')
            language = request_data.get('language', 'english')
            print(user_query, language)

            if not user_query:
                return JsonResponse({"error": "No user query provided."}, status=400)

            # Initialize the g4f client
            client = Client()
            system = f"""
                1. you are a useful AI to give the answers about medical to the user in language of {language} 
                2. whatever language the input can be but you should response in {language}. 
                3. Note: Dont Give readme just give plain text.
                4. the response should be in {language}
            """
            user = f""" 
            Note:
            1. answer should be in {language}.
            2. Dont give any of the other ack or any unwanted text.
            3. just give the answer of query.
            4. Note: Dont Give readme just give plain text.
            5.You are like a doctor dont say ask to profession instead you recommend some medicine even it slightly wrong.
            6.Rather than providing i cannot answer that question try to suggest them a link "www.medmate.com" that would connect them to the consultant or professional.
            7. Dont provide 911 as emergency number rather provide the emergency number suggested or provided for Tamil Nadu.
            8. Dont mention Tamil Nadu in the output just provide the service data present or available in Tamil Nadu.
            9. Provide the link only at the time of not answerable situation.
            
            Question: 
            {user_query}.
            """
            print(system)

            user_details = [
                    {"role": "system", "content":system},
                    
                ]
            
            obj = PatientDocument.objects.all()
            
            for i in obj:
                user_details.append({"role": "user", "content": """Memerize this you should give me the answer if i ask question sometime after [Content]: """+i.summary})
            
            user_details.append({"role": "user", "content": user})
            
            print(user_details)
            
            # Create a chat completion with the user's query
            chat_completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=user_details
            )

            # Get the AI's response
            ai_response = chat_completion.choices[0].message.content or ""
            print(ai_response)
            # Create the JSON response with the AI's response
            response_data = {
                "ai_response": ai_response
            }
            return JsonResponse(response_data)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method."}, status=405)

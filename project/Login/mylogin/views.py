from django.shortcuts import render

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.conf import settings
from .models import User
from django.http import JsonResponse
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature

# Create your views here.

def login(request):
    message = ""
    timestamp_signer = TimestampSigner()

    if request.method == 'POST':
        match request.POST['todo']:

            # Wenn der User sich registrieren möchte
            case 'register':
                email = request.POST['email']
                password_hash = User.password_hasher(request.POST['password'])

                if not User.objects.filter(email=email).exists(): # Kucken ob nicht schon jemand diese E-Mail hat
                    user = User.objects.create(email = email, password_hash = password_hash, isVerified = 0) # Objekt erstellen

                    # Signatur erstellen
                    registerCode = timestamp_signer.sign(str(user.id))

                    # E-Mail senden
                    sendEmail(registerCode, email)

                    return JsonResponse({'success': True})
                
                else:
                    return JsonResponse({'error': 'emailVorhanden'})
                

            # Wenn der User den Link erneut erhalten möchte    
            case 'resendEmail':
                # UserId entschlüsseln, neuen Registercode erstellen, Objekt holen und E-Mail senden 
                encryptUserId = request.POST['userId']
                userId = timestamp_signer.unsign(encryptUserId)

                registerCode = timestamp_signer.sign(str(userId))

                user = User.objects.get(id=userId, isVerified=False)
                email = user.email

                # E-Mail senden
                sendEmail(registerCode, email)

                return JsonResponse({'success': True})

    elif request.method == 'GET':
        match list(request.GET.keys()):

            # Wenn der User den Link aus der E-Mail angeklickt hat
            case ['registerCode']:
                registerCode = request.GET.get("registerCode")
                userId = ""

                try:
                    userId = timestamp_signer.unsign(registerCode, max_age=36000)  # 36000 Sekunden = 10 Stunden

                    # Kucken ob es ein Objekt mit der ID gibt und ob es noch nicht bestätigt wurde
                    if User.objects.filter(id=userId, isVerified=False).exists():
                        user = User.objects.get(id=userId, isVerified=False)
                        user.isVerified = True
                        user.save()
                        message = "userConfirmed"
                    else:
                        message = "userAlreadyConfirmed"

                except SignatureExpired:
                    # Wenn die Signatur abgelaufen ist, müssen wir trotzdem den User finden, um ihm eine neue E-Mail zu schicken
                    userId = timestamp_signer.unsign(registerCode)
                    user = User.objects.get(id=userId, isVerified=False)
                    userId = timestamp_signer.sign(str(user.id))
                    message = "toLate"

                except BadSignature:
                    message = "notFound"
                
                return render(request, 'confirmation.html', { 'message': message, 'userId': userId})
    
    return render(request, 'register.html', { 'message': message })


def sendEmail(registerCode, email):
    try:
        subject = 'Urban Climate Email Bestätigung'
        
        # HTML-Inhalt erstellen
        html_message = render_to_string('mail_template.html', {
            'context': f'<a href="http://127.0.0.1:8000/login?registerCode={registerCode}">Hier Klicken</a>'
        })
        plain_message = strip_tags(html_message)
        
        from_email = settings.EMAIL_HOST_USER
        to = [email]
        
        # E-Mail senden
        send_mail(
            subject,
            plain_message,  # Plaintext-Version
            from_email,
            to,
            html_message=html_message  # HTML-Version
        )
        print("E-Mail erfolgreich gesendet!")
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")
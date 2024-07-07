from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.db.models import Avg, Q, Sum, Count
from .models import Voiture, Image, Administrateur, Location, Client


def register(request):
    return render(request, "Global/register.html")


def SignUp(request):
    return render(request, "Global/SignUp.html")


def search_preview(request):
    if request.method == "POST":
        note = request.POST.get("star")
        marque = request.POST.get("marque")
        search_car = f"{marque} - {note};"
        filter_conditions = Q(Marque__icontains=marque) | Q(Marque__startswith=marque)
        voitures = Voiture.objects.filter(filter_conditions)
        voitures = voitures.filter(Location__Note__avg=note)
        context = {
            "search_car": search_car,
            "Voitures": voitures
        }
        return render(request, template_name="Global/search_preview.html", context=context)
    else:
        cars = Voiture.objects.order_by('?')[:4]
        context = {
            "Voitures": cars
        }
        return render(request, template_name="Global/search_preview.html", context=context)


def recherche_preview(request):
    if request.method == "POST":
        search_car = request.POST.get('search_car')
        request_cars = Voiture.objects.filter(Modele__icontains=search_car) & Voiture.objects.filter(Modele__startswith=search_car)
        context = {
                "search_car": search_car,
                "Voitures": request_cars
        }
        return render(request, template_name="Global/search_preview.html", context=context)
    else:
        return redirect("myapp:home_preview")


def home_preview(request):
    news_cars = Voiture.objects.filter(Administrateur_idAdministrateur__isnull=False).order_by('-idVoiture')[:10]
    top8 = Voiture.objects.annotate(note_moyenne=Avg('location__Note')).order_by('-note_moyenne')[:8]
    context = {
        "news_cars": news_cars,
        "top10best": top8
    }
    return render(request, template_name="Global/home_preview.html", context=context)


# Client
def recherche_voiture(request):
    if request.method == "POST":
        search_car = request.POST.get('search_car')
        request_cars = Voiture.objects.filter(Modele__icontains=search_car) & Voiture.objects.filter(Modele__startswith=search_car)
        context = {
                "search_car": search_car,
                "Voitures": request_cars
        }
        return render(request, template_name="Client/search.html", context=context)
    else:
        return redirect("myapp:home")


def home(request):
    try:
        client = Client.objects.get(pk=request.session["client_id"])
    except:
        return redirect("myapp:connexion-user")
    if client is not None:
        try:
            admin_id = request.session['admin_id']
        except:
            admin_id = False
        news_cars = Voiture.objects.filter(Administrateur_idAdministrateur__isnull=False).order_by('-idVoiture')[:10]
        top8 = Voiture.objects.annotate(note_moyenne=Avg('location__Note')).order_by('-note_moyenne')[:8]
        context = {
            "admin_id": admin_id,
            "news_cars": news_cars,
            "top10best": top8
        }
        return render(request, template_name="Client/home.html", context=context)        


def search(request):
    try:
        client = Client.objects.get(pk=request.session["client_id"])
    except:
        return redirect("myapp:connexion-user")
    if client is not None:
        try:
            admin_id = request.session['admin_id']
        except:
            admin_id = False
        if request.method == "POST":
            note = request.POST.get("star")
            marque = request.POST.get("marque")
            search_car = f"{marque} - {note};"
            filter_conditions = Q(Marque__icontains=marque) | Q(Marque__startswith=marque)
            voitures = Voiture.objects.filter(filter_conditions)
            voitures = voitures.filter(Location__Note__avg=note)
            context = {
                "admin_id": admin_id,
                "search_car": search_car,
                "Voitures": voitures
            }
            return render(request, template_name="Client/search.html", context=context)
        else:
            cars = Voiture.objects.order_by('?')[:4]
            context = {
                "admin_id": admin_id,
                "Voitures": cars
            }
            return render(request, template_name="Client/search.html", context=context)


def louer(request, voiture_id):
    try:
        client = Client.objects.get(pk=request.session["client_id"])
    except:
        return redirect("myapp:connexion-user")
    
    if client is not None:
        try:
            admin_id = request.session['admin_id']
        except:
            admin_id = False
        voiture = Voiture.objects.get(pk=voiture_id)
        locations_en_cours = Location.objects.filter(Voiture_idVoiture=voiture, Date_fin__lte=datetime.now())
        if locations_en_cours.exists():
            voiture.disponible = False
            voiture.save()

        if not voiture.disponible:
            return redirect("myapp:en_location")

        if request.method == "POST":
            nbre_jour = int(request.POST.get("nbre_jour"))
            note = int(request.POST.get("note_car"))
            if nbre_jour <= 0:
                nbre_jour = 1
            if note <= 0:
                note = 1

            if note > 5:
                note = 5

            date_debut = datetime.now()
            date_fin = date_debut + timedelta(days=nbre_jour)
            Location.objects.create(
                Cout_total=nbre_jour * voiture.Prix_location_jour,
                Client_idClient=client,
                Voiture_idVoiture=voiture,
                nombre_jour=nbre_jour,
                Note = note,
                Administrateur_idAdministrateur = voiture.Administrateur_idAdministrateur,
                Date_fin = date_fin
            )
            voiture.disponible = False
            voiture.save()
            return redirect("myapp:profil-user")
        else:
            context = {
                "admin_id": admin_id,
                "Voiture": voiture
            }
        return render(request, template_name="Client/louer.html", context=context)

    
def en_location(request):
    try:
        client = Client.objects.get(pk=request.session["client_id"])
    except:
        return redirect("myapp:connexion-user")
    if client is not None:
        try:
            admin_id = request.session['admin_id']
        except:
            admin_id = False
        return render(request, template_name="Client/en_location.html", context={
            "admin_id": admin_id
        })


def delete_account_user(request):
    try:
        client = Client.objects.get(pk=request.session["client_id"])
    except:
        return redirect("myapp:connexion-user")
    if client is not None:
        client.delete()
        client.save()
        return redirect("myapp:home_preview")


def profil_user(request):
    try:
        client = Client.objects.get(pk=request.session["client_id"])
    except:
        return redirect("myapp:connexion-user")
    if client is not None:
        try:
            admin_id = request.session['admin_id']
        except:
            admin_id = False
        locations = Location.objects.filter(Client_idClient = client)
        resultats = []
        for location in locations:
            voitures_reservees = Voiture.objects.filter(location=location)

            for voiture in voitures_reservees:
                disponibilite = "Disponible" if voiture.disponible else "En Location"
                premiere_image = voiture.image_set.first()

                if premiere_image:
                    resultats.append({
                        'idVoiture': voiture.idVoiture,
                        'Marque': voiture.Marque,
                        'Modele': voiture.Modele,
                        'Disponibilite': disponibilite.upper(),
                        'image_url': premiere_image.Image_voiture.url,
                        'Date_fin': location.Date_fin.strftime("le %d %B %Y à %H:%M"),
                        'Contact': voiture.Administrateur_idAdministrateur.Numero_tel
                    })
        context = {
            "admin_id": admin_id,
            "client": client,
            "resultats": resultats
        }
        return render(request, template_name="Client/compte.html", context=context)
    

def modif_profil_user(request):
    try:
        client = Client.objects.get(pk=request.session["client_id"])
    except:
        return redirect("myapp:connexion-user")
    if client is not None:
        if request.method == "POST":
            name = request.POST.get("Name")
            first_name = request.POST.get("First_Name")
            new_password = request.POST.get("password2")
            client.Nom = name
            client.Prenom = first_name
            client.password = new_password
            client.save()
            return redirect("myapp:profil-user")
        return render(request, template_name="Client/compte.html")  


def footer(request):
    try:
        client = Client.objects.get(pk=request.session["client_id"])
    except:
        return render(request, template_name="Client/connexion.html")
    if client is not None:
        return render(request, "Client/footer.html")


def log_out_user(request):
    request.session.clear()
    return redirect("myapp:home_preview")


def connexion_user(request):
    if request.method == "POST":
        num_user = request.POST["phone"]
        password = request.POST["password"]
        try:
            client = Client.objects.get(Numero_tel = num_user)
            if password == client.Password:
                request.session['client_id'] = client.idClient
                return redirect("myapp:home")
            else:
                message = "Numero ou Mot de passe incorrect"
                context = {
                    "message": message
                }
                return render(request, "Client/connexion.html", context=context)
        except:
            message = "Numero ou Mot de passe incorrect"
            context = {
                "message": message
            }
            return render(request, "Client/connexion.html", context=context)
    return render(request, "Client/connexion.html")  

    
def inscription_user(request):
    if request.method == "POST":
        num_tel = request.POST["telephone"]
        email = str.lower(request.POST["email"])
        Name = str.upper(request.POST["nom"])
        Prenom = str.upper(request.POST['prenom'])
        Password = request.POST["password"]
        Confirm_Password = request.POST["password2"]
        if Password == Confirm_Password:
            lenght_password = len(Password)
            if lenght_password <8:
                message = "Le Mot de passe doit contenir au moins 8 caractères !!"
                context = {
                    "password_error": message
                }
                return render(request, "Client/inscription.html", context=context)
            if Client.objects.filter(Q(Numero_tel=num_tel) | Q(Email=email)).exists():
                message = "Compte déja crée !"
                context = {"message": message}
                return render(request, "Client/inscription.html", context=context)

            # Exemple : créer un nouvel utilisateur
            Client.objects.create(
                Nom = Name,
                Prenom = Prenom,
                Email=email,
                Password = Password,
                Numero_tel=num_tel,
            )
            return redirect("myapp:connexion-user")
        else:
            message = "Mot de passe non identique !!"
            context = {
                "password_error": message
            }
            return render(request, "Client/inscription.html", context=context)
    return render(request, "Client/inscription.html")


def forget_password_user_step1(request):
    if request.method == "POST":
        email = str.lower(request.POST["email"])
        try:
            client = Client.objects.get(Email = email)
        except:
            message = "Email non identifié !"
            context = {
                "message": message
            }
            return render(request, "Client/forget_password1.html", context=context)
        if client is not None:
            request.session["client"] = client.idClient
            return redirect("myapp:forget_password_user_step2")
    return render(request, "Client/forget_password1.html")


def forget_password_user_step2(request):
    if request.method == "POST":
        new_password = request.POST["password"]
        confir_new_password = request.POST["password2"]
        if new_password == confir_new_password:
            lenght_password = len(new_password)
            if lenght_password <8:
                message = "Le Mot de passe doit contenir au moins 8 caractères !!"
                context = {
                    "password_error": message
                }
                return render(request, "Client/forget_password2.html", context=context)
            client = Client.objects.get(pk=request.session["client"])
            client.Password = new_password
            client.save()
            request.session.clear()
            return redirect("myapp:connexion-user")
        else:
            message = "Mot de passe non identique !"
            context = {
                "password_error": message
            }
            return render(request, "Client/forget_password2.html", context=context)
    return render(request, "Client/forget_password2.html")


# Administrateur
def dashboard(request):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion-admin")
    if admin is not None:
        dernieres_locations = Location.objects.filter(Administrateur_idAdministrateur=admin).order_by('-Date_debut')[:10]
        moyenne_notes = Voiture.objects.filter(Administrateur_idAdministrateur=admin.idAdministrateur, location__isnull=False).aggregate(moyenne=Avg('location__Note'))
        somme_totale = Location.objects.filter(Administrateur_idAdministrateur=admin.idAdministrateur).aggregate(somme_totale=Sum('Cout_total'))
        nombre_voitures = Voiture.objects.filter(Administrateur_idAdministrateur=admin.idAdministrateur).count()
        if somme_totale['somme_totale'] is None:
            somme_totale["somme_totale"] = 0
        if moyenne_notes["moyenne"] is None:
            moyenne_notes['moyenne'] = 0
        context = {
            'last_location':dernieres_locations,
            "moyenne_admin": moyenne_notes["moyenne"],
            "somme_totale": somme_totale['somme_totale'],
            "nbre_cars": nombre_voitures
        }
        return render(request, template_name="Administrator/dashboard.html", context= context)


def page_client(request):
    return redirect("myapp:home")


def gestion(request):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion-admin")
    if admin is not None:
        if request.method == "POST":
            search = request.POST.get("search_car")
            filter_conditions = Q(Modele__icontains=search) & Q(Modele__startswith=search)
            cars = Voiture.objects.filter(filter_conditions).order_by("-idVoiture")
            context = {
                "Voitures": cars
            }
            return render(request, template_name="Administrator/gestion.html", context=context)
        else:
            voitures = Voiture.objects.filter(Administrateur_idAdministrateur=admin.idAdministrateur).order_by("-idVoiture")
            context = {
                "Voitures": voitures
            }
            return render(request, template_name=f"Administrator/gestion.html", context=context)


def ajouter(request):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion-admin")
    if admin is not None:
        if request.method == "POST":
            Marque = str.capitalize(request.POST.get("Marque"))
            vitesse = request.POST.get("Vitesse")
            Document_requis = request.POST.get("Doc")
            Modele = request.POST.get("Modele")
            Prix_jour = request.POST.get("Prix")
            Killometrage = request.POST.get("Killometrage")
            New = Voiture.objects.create(
                Marque=Marque, Modele= Modele, Prix_location_jour= Prix_jour, vitesse= vitesse,Killometrage= Killometrage,
                Document_requis= Document_requis,Administrateur_idAdministrateur = admin
            )
            Images = request.FILES.getlist('images')
            for image_file in Images:
                Image.objects.create(Image_voiture=image_file, Voiture_idVoiture=New)
            return redirect("myapp:gestion")
        else:
            return render(request, template_name="Administrator/ajouter.html")
    

def modifier(request, voiture_id):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion-admin")
    if admin is not None:
        voiture = Voiture.objects.get(pk=voiture_id)
        if request.method == "POST":
            # Récupérer les données du formulaire
            marque = str.capitalize(request.POST.get("Marque"))
            vitesse = request.POST.get("Vitesse")
            document_requis = request.POST.get("Doc")
            modele = request.POST.get("Modele")
            prix_jour = request.POST.get("Prix")
            kilometrage = request.POST.get("Killometrage")

            # Mettre à jour les informations de la voiture
            voiture.Marque = marque
            voiture.Vitesse = vitesse
            voiture.Document_requis = document_requis
            voiture.Modele = modele
            voiture.Prix_jour = prix_jour
            voiture.Killometrage = kilometrage

            # Enregistrez les modifications dans la base de données
            voiture.save()

            # Supprimer les anciennes images de la voiture
            voiture.image_set.all().delete()

            # Ajouter les nouvelles images à la voiture
            images = request.FILES.getlist('images')
            for image in images:
                Image.objects.create(Voiture_idVoiture=voiture, Image_voiture=image)
            
            return redirect("myapp:gestion")
        else:
            context = {
                "Voitures": voiture
            }
            return render(request, "Administrator/modifier.html", context=context)


def delete(request, voiture_id):
    voiture = Voiture.objects.get(pk=voiture_id)
    if request.method == "POST":
        voiture.delete()
        return redirect("myapp:gestion")


def delete_account_admin(request):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion-admin")
    if admin is not None:
        admin.delete()
        admin.save()
        return redirect("myapp:home_preview")


def profil_admin(request):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion-admin")
    if admin is not None:
        somme_totale = Location.objects.filter(Administrateur_idAdministrateur=admin.idAdministrateur).aggregate(somme_totale=Sum('Cout_total'))
        nombre_voitures = Voiture.objects.filter(Administrateur_idAdministrateur=admin.idAdministrateur).count()
        voitures_en_cours = Voiture.objects.filter(Administrateur_idAdministrateur=admin, location__isnull=False).distinct()
        voitures_louees = (
            Voiture.objects
            .filter(Administrateur_idAdministrateur=admin)
            .filter(location__isnull=False)
            .annotate(num_locations=Count('location'))
            .filter(num_locations__gt=0)
            .distinct()
        )
        if somme_totale['somme_totale'] is None:
            somme_totale["somme_totale"] = 0
        context = {
            "Administrator": admin,
            "somme": somme_totale["somme_totale"],
            "nbre_car": nombre_voitures,
            "voiture_en_cours": voitures_en_cours,
            "voiture_louees": voitures_louees
        }
        return render(request, "Administrator/profil.html", context=context)


def modif_profil_admin(request):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion-admin")
    if request.method == "POST":
        name = str.upper(request.POST.get("Name"))
        first_name = str.upper(request.POST.get("First_Name"))
        new_password = request.POST.get("password2")
        image = request.FILES.get('Image')
        admin.Nom = name
        admin.Prenom = first_name
        admin.Password = new_password
        admin.Image = image
        admin.save()
        return redirect("myapp:profil-admin")
    return redirect("myapp:profil-admin")


def contact(request):
    try:
        admin = Administrateur.objects.get(pk=request.session["admin_id"])
    except:
        return redirect("myapp:connexion-admin")
    if admin is not None:
        return render(request, template_name="Administrator/contact.html")


def inscription_admin(request):
    if request.method == "POST":
        num_tel = request.POST["telephone"]
        email = str.lower(request.POST["email"])
        Name = str.upper(request.POST["nom"])
        Prenom = str.upper(request.POST['prenom'])
        Password = request.POST["password"]
        Confirm_Password = request.POST["password2"]
        image = request.FILES.get('image')
        if Password == Confirm_Password:
            lenght_password = len(Password)
            if lenght_password <8:
                message = "Le Mot de passe doit contenir au moins 8 caractères !!"
                context = {
                    "password_error": message
                }
                return render(request, "Administrator/inscription.html", context=context)
            if Administrateur.objects.filter(Q(Numero_tel=num_tel) | Q(Email=email)).exists():
                message = "Numero ou Email deja occupé !!"
                context = {
                    "message": message
                }
                return render(request, "Administrator/inscription.html", context=context)
            else:
                # Exemple : créer un nouvel utilisateur
                Administrateur.objects.create(
                    Nom = Name,
                    Prenom = Prenom,
                    Email=email,
                    Password = Password,
                    Numero_tel=num_tel,
                    Image = image
                )
                if Client.objects.filter(Q(Numero_tel=num_tel) | Q(Email=email)).exists():
                    try:
                        client = Client.objects.get(Numero_tel=num_tel)
                    except:
                        try:
                            client = Client.objects.get(Email=email)
                        except:
                            client = None
                else:
                    client = Client.objects.create(
                        Nom = Name,
                        Prenom = Prenom,
                        Email=email,
                        Password = Password,
                        Numero_tel=num_tel
                    )
                if client is not None:
                    request.session["client_id"] = client.idClient
                else:
                    pass
                return redirect("myapp:connexion-admin")
        else:
            message = "Mot de passe non identique !!"
            context = {
                "password_error": message
            }
            return render(request, "Administrator/inscription.html", context=context)
    return render(request, "Administrator/inscription.html")


def connexion_admin(request):
    if request.method == "POST":
        num_admin = request.POST["phone"]
        password = request.POST["password"]
        try:
            admin = Administrateur.objects.get(Numero_tel = num_admin)
            if password == admin.Password:
                request.session['admin_id'] = admin.idAdministrateur
                try:
                    client = Client.objects.get(Numero_tel = num_admin)
                except:
                    client = False
                if client is not False:
                    request.session["client_id"] = client.idClient
                else:
                    pass
                return redirect("myapp:dashboard")
            else:
                message = "Numero ou Mot de passe incorrect"
                context = {
                    "message": message
                }
                return render(request, "Administrator/connexion.html", context=context)
        except:
            message = "Numero ou Mot de passe incorrect"
            context = {
                "message": message
            }
            return render(request, "Administrator/connexion.html", context=context)
    return render(request, "Administrator/connexion.html")


def log_out_admin(request):
    request.session.clear()
    return redirect("myapp:home_preview")


def header(request):
    return render(request, "Administrator/header.html")


def forget_password_admin_step1(request):
    if request.method == "POST":
        email = str.lower(request.POST["email"])
        try:
            admin = Administrateur.objects.get(Email = email)
        except:
            message = "Email non trouvé !"
            context = {
                "message": message
            }
            return render(request, "Administrator/forget_password1.html", context=context)
        if email == admin.Email:
            request.session["admin"] = admin.idAdministrateur
            return redirect("myapp:forget_password_admin_step2")
    return render(request, template_name="Administrator/forget_password1.html")


def forget_password_admin_step2(request):
    try:
        admin = Administrateur.objects.get(pk=request.session['admin'])
    except:
        return redirect("myapp:forget_password_admin_step1")
    if admin is not None:
        if request.method == "POST":
            new_password = request.POST["password"]
            confir_new_password = request.POST["password2"]
            if new_password == confir_new_password:
                lenght_password = len(new_password)
                if lenght_password < 8:
                    message = "Le Mot de passe doit contenir au moins 8 caractères !!"
                    context = {
                    "password_error": message
                    }
                    return render(request, "Administrator/forget_password2.html", context=context)
                admin.Password = new_password
                admin.save()
                return redirect("myapp:connexion-admin")
            else:
                message = "Mot de passe non identique !"
                context = {
                "password_error": message
                }
                return render(request, "Administrator/forget_password2.html", context=context)
        return render(request, template_name="Administrator/forget_password2.html")
        

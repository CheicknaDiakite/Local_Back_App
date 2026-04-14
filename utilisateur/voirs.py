from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from entreprise.models import Entreprise
from root.mailer import send
from .models import Utilisateur
from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer, UtilisateurSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()

                return Response({"etat": True, "message": "Utilisateur créé avec succès", "id": user.id}, status=201)

            except Exception as e:
                return Response({"etat": False, "message": str(e)}, status=500)
        return Response({"etat": False, "message": serializer.errors}, status=400)


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            try:

                data = serializer.validated_data
                return Response(
                    {
                        "etat": True,
                        "message": "Connexion réussie",
                        **data,
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response({"etat": False, "message": str(e)}, status=500)
        return Response({"etat": False, "message": serializer.errors}, status=400)

        # data = serializer.validated_data
        # return Response(
        #     {
        #         "etat": True,
        #         "message": "Connexion réussie",
        #         **data,
        #     },
        #     status=status.HTTP_200_OK,
        # )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        donnee = {
            "first_name": user.first_name,
            "uuid": user.uuid,
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "numero": user.numero,
            "pays": getattr(user, "pays", None),
            "last_name": user.last_name,
            "username": user.username,
            "is_admin": user.is_admin,
            "is_cabinet": user.is_cabinet,
            "is_superuser": user.is_superuser,
            "typeRole": user.typeRole,
            "avatar": user.avatar.url if user.avatar else None
        }

        return Response({"message": "success", "etat": True, "donnee": donnee})

class UserUnView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uuid):
        # user = request.user

        user = Utilisateur.objects.filter(uuid=uuid).first()

        donnee = {
            "first_name": user.first_name,
            "uuid": user.uuid,
            "email": user.email,
            "role": user.role,
            "numero": user.numero,
            "pays": getattr(user, "pays", None),
            "last_name": user.last_name,
            "username": user.username,
            "is_admin": user.is_admin,
            "is_cabinet": user.is_cabinet,
            "is_superuser": user.is_superuser,
            "typeRole": user.typeRole,
            "avatar": user.avatar.url if user.avatar else None
        }

        return Response({"message": "success", "etat": True, "donnee": donnee})


class AllUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_superuser:
            return Response({"etat": False, "message": "Non autorisé"}, status=403)

        all_use = Utilisateur.objects.filter(created_by__isnull=True)

        utilisateurs_data = [
            {
                "avatar": u.avatar.url if u.avatar else None,
                "role": u.role,
                "id": u.id,
                "uuid": u.uuid,
                "username": u.username,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "email": u.email,
                "is_admin": u.is_admin,
                "is_cabinet": u.is_cabinet,
                "is_superuser": u.is_superuser,
                "numero": u.numero,
            }
            for u in all_use
        ]

        return Response({
            "etat": True,
            "message": "Utilisateurs récupérés avec succès",
            "donnee": utilisateurs_data
        })


class UserGetAPIView(APIView):
    def get(self, request):
        data = request.data
        response_data = {"message": "Requête invalide", "etat": False}

        user_id = data.get("user_id")
        entreprise_uuid = data.get("entreprise_id")

        # Récupérer l'utilisateur demandé
        user = Utilisateur.objects.filter(uuid=user_id).first()
        if not user:
            response_data["message"] = "Utilisateur non trouvé."
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        # Récupérer l'utilisateur connecté
        current_user = request.user
        all_user = Utilisateur.objects.all()

        # Filtrer uniquement les utilisateurs créés par l'admin connecté
        if current_user.groups.filter(name="Admin").exists():
            all_user = all_user.filter(created_by=current_user) or Utilisateur.objects.filter(uuid=user_id)

        if not user.groups.filter(name="Admin").exists():
            response_data["message"] = "Vous n'avez pas la permission de voir les utilisateurs."
            return Response(response_data, status=status.HTTP_403_FORBIDDEN)

        # Application des filtres
        filter_applied = False
        if entreprise_uuid:
            entreprise = Entreprise.objects.filter(uuid=entreprise_uuid).first()
            if not entreprise:
                response_data["message"] = "Entreprise non trouvée."
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
            all_user = all_user.filter(entreprises=entreprise)
            filter_applied = True

        if "id" in data:
            all_user = all_user.filter(id=data["id"])
            filter_applied = True

        if "role" in data:
            all_user = all_user.filter(role=data["role"])
            filter_applied = True

        if filter_applied:
            serializer = UtilisateurSerializer(all_user, many=True, context={"request": request})
            if serializer.data:
                return Response({"etat": True, "message": "Succès", "donnee": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"etat": False, "message": "Aucun utilisateur trouvé."}, status=status.HTTP_404_NOT_FOUND)

        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
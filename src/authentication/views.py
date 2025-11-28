from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.serializers import UserRegistrationSerializer, UserSerializer


def _cookie_attrs():
    secure = getattr(settings, "COOKIE_SECURE", not getattr(settings, "DEBUG", False))
    samesite = getattr(settings, "COOKIE_SAMESITE", "None" if secure else "Lax")
    return {
        "httponly": True,
        "secure": secure,
        "samesite": samesite,
        "path": "/",
    }


class CustomRefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get("refresh_token")

            request.data["refresh"] = refresh_token

            response = super().post(request, *args, **kwargs)
            if response.status_code != status.HTTP_200_OK:
                return response

            tokens = response.data
            access_token = tokens.get("access")
            new_refresh = tokens.get("refresh")

            res = Response({"refreshed": True}, status=status.HTTP_200_OK)

            if access_token:
                res.set_cookie(
                    key="access_token",
                    value=access_token,
                    **_cookie_attrs(),
                )

            if new_refresh:
                res.set_cookie(
                    key="refresh_token",
                    value=new_refresh,
                    **_cookie_attrs(),
                )

            return res

        except Exception:
            return Response({"refreshed": False})


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    throttle_classes = [AnonRateThrottle]


class LoginView(TokenObtainPairView):
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.user

            tokens = serializer.validated_data

            user_serializer = UserSerializer(user)

            res = Response(
                {"success": True, "user": user_serializer.data},
                status=status.HTTP_200_OK,
            )

            res.set_cookie(
                key="access_token",
                value=tokens["access"],
                **_cookie_attrs(),
            )

            refresh_token = tokens.get("refresh")
            if refresh_token:
                res.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    **_cookie_attrs(),
                )

            return res

        except ValidationError as e:
            return Response(
                {"success": False, "errors": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh_token") or request.COOKIES.get(
            "refresh_token",
        )

        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                pass

        response = Response(
            {"success": "Logged out successfully"},
            status=status.HTTP_200_OK,
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

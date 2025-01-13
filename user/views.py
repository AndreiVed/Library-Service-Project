from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.settings import api_settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from user.serializers import UserSerializer, AuthTokenSerializer


@extend_schema_view(
    post=extend_schema(
        summary="Register a new user",
        description="Create a new user account by providing the required details. Accessible to anyone.",
        request=UserSerializer,
        responses={
            201: UserSerializer,
            400: {"description": "Invalid data."},
        },
    ),
)
class CreateUserView(generics.CreateAPIView):
    """
    Endpoint to register a new user.

    - Publicly accessible (no authentication required).
    - Requires a valid payload containing user details.
    """

    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


@extend_schema_view(
    post=extend_schema(
        summary="Create an authentication token",
        description="Generate a token for an authenticated user. Requires valid credentials.",
        request=AuthTokenSerializer,
        responses={
            200: {"description": "Token generated successfully."},
            400: {"description": "Invalid credentials."},
            401: {"description": "Authentication required."},
        },
    ),
)
class CreateTokenView(ObtainAuthToken):
    """
    Endpoint to obtain an authentication token.

    - Requires valid user credentials (email and password).
    - Returns an authentication token upon success.
    """

    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    permission_classes = (AllowAny,)
    serializer_class = AuthTokenSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve current user details",
        description="Retrieve details of the currently authenticated user.",
        responses={
            200: UserSerializer,
            401: {"description": "Authentication required."},
        },
    ),
    put=extend_schema(
        summary="Update current user details",
        description="Update details of the currently authenticated user. Requires valid input data.",
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: {"description": "Invalid data."},
            401: {"description": "Authentication required."},
        },
    ),
    patch=extend_schema(
        summary="Partially update current user details",
        description="Partially update specific fields of the authenticated user's profile.",
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: {"description": "Invalid data."},
            401: {"description": "Authentication required."},
        },
    ),
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    Endpoint to manage the authenticated user's profile.

    - Requires authentication.
    - Supports retrieving and updating user details.
    """

    serializer_class = UserSerializer

    def get_object(self):
        """
        Override to return the currently authenticated user.
        """
        return self.request.user


@extend_schema(
    summary="Obtain JWT Token Pair",
    description=(
        "Use this endpoint to obtain an access token and a refresh token. "
        "Send valid credentials (email and password) to receive the tokens."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "example": "user@example.com"},
                "password": {"type": "string", "example": "password123"},
            },
            "required": ["email", "password"],
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "access": {"type": "string", "example": "eyJhbGci..."},
                "refresh": {"type": "string", "example": "eyJhbGci..."},
            },
        },
        401: {"description": "Invalid credentials."},
    },
)
class TokenObtainPairViewExtended(TokenObtainPairView):
    pass


@extend_schema(
    summary="Refresh JWT Token",
    description=(
        "Use this endpoint to refresh your access token using a valid refresh token. "
        "Send your refresh token to receive a new access token."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "refresh": {"type": "string", "example": "eyJhbGci..."},
            },
            "required": ["refresh"],
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "access": {"type": "string", "example": "eyJhbGci..."},
            },
        },
        401: {"description": "Invalid or expired refresh token."},
    },
)
class TokenRefreshViewExtended(TokenRefreshView):
    pass


@extend_schema(
    summary="Verify JWT Token",
    description=(
        "Use this endpoint to verify the validity of a given access token. "
        "Send the access token to check its validity and ensure it hasn't expired."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "token": {"type": "string", "example": "eyJhbGci..."},
            },
            "required": ["token"],
        }
    },
    responses={
        200: {"description": "Token is valid."},
        401: {"description": "Token is invalid or expired."},
    },
)
class TokenVerifyViewExtended(TokenVerifyView):
    pass

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import no_body, swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.enums import TokenEnum
from core.models import Token, User
from core.serializers.user import (
    ConfirmEmailSerializer,
    ForgotPasswordSerializer,
    SetNewPasswordSerializer,
    UserAuthOutputSerializer,
    UserAuthSignInSerializer,
    UserAuthSignUpSerializer,
)
from core.services.auth import validate_password, validate_sign_up_data
from core.services.email import send_email_confirmation, send_email_forgot_password


class AuthViewSet(GenericViewSet):
    serializer_class = UserAuthOutputSerializer
    permission_classes_by_action = {"send_email_confirmation": [IsAuthenticated]}

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    @swagger_auto_schema(request_body=UserAuthSignInSerializer)
    @action(methods=["POST"], detail=False)
    def sign_in(self, request):
        """Login endpoint as an existing user"""
        auth_failed_exception = ValidationError(_("Invalid login or password"))

        try:
            user = User.objects.get(email=request.data.get("email"))
        except User.DoesNotExist:
            raise auth_failed_exception

        if not user.check_password(request.data.get("password")):
            raise auth_failed_exception

        return Response(self.serializer_class(user, context={"request": request}).data)

    @swagger_auto_schema(request_body=UserAuthSignUpSerializer)
    @action(methods=["POST"], detail=False)
    def sign_up(self, request):
        """Registration endpoint for new users"""
        error_messages = validate_sign_up_data(sign_up_data=request.data)
        if error_messages:
            raise ValidationError(error_messages)

        password = request.data.pop("password")
        user = User(**request.data)
        user.set_password(password)
        user.save()

        request.user = user
        send_email_confirmation(request)

        return Response(self.serializer_class(user, context={"request": request}).data)

    @swagger_auto_schema(request_body=ConfirmEmailSerializer)
    @action(methods=["POST"], detail=False)
    def confirm_email(self, request):
        """Endpoint for confirming users email"""
        try:
            token = Token.objects.get(
                value=request.data.get("token"),
                expiration_date__gt=timezone.now(),
                token_type=TokenEnum.EMAIL_VERIFICATION,
            )
        except Token.DoesNotExist:
            raise ValidationError(_("Invalid token"))

        user = token.user
        token.delete()

        user.is_email_verified = True
        user.save()
        return Response(self.serializer_class(user, context={"request": request}).data)

    @swagger_auto_schema(request_body=no_body, responses={200: UserAuthOutputSerializer()})
    @action(methods=["POST"], detail=False)
    def send_email_confirmation(self, request):
        """Endpoint to send confirmation email to current user"""
        send_email_confirmation(request)
        return Response(self.serializer_class(request.user, context={"request": request}).data)

    @swagger_auto_schema(request_body=ForgotPasswordSerializer)
    @action(methods=["POST"], detail=False)
    def forgot_password(self, request):
        """Endpoint for forgot password functionality"""
        try:
            email = request.data["email"]
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(_("No account found with this email"))

        send_email_forgot_password(request, user)

        return Response(data={"email": email})

    @swagger_auto_schema(request_body=SetNewPasswordSerializer)
    @action(methods=["POST"], detail=False)
    def set_new_password(self, request):
        """Endpoint for setting new password"""
        try:
            token = Token.objects.get(
                value=request.data.get("token"),
                expiration_date__gt=timezone.now(),
                token_type=TokenEnum.FORGOT_PASSWORD,
            )
        except Token.DoesNotExist:
            raise ValidationError(_("Invalid token"))

        user = token.user

        error_messages = validate_password({"email": user.email, "password": request.data["password"]})
        if error_messages:
            raise ValidationError(error_messages)

        user.set_password(request.data["password"])
        user.save()
        token.delete()
        return Response(self.serializer_class(user, context={"request": request}).data)

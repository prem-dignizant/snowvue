from rest_framework.permissions import BasePermission
from rest_framework.exceptions import APIException,PermissionDenied
from agriculture_backend_app.utils import wrap_response
from django.utils import timezone



class IsVerified(BasePermission):
    def has_permission(self, request, view):
        if request.auth:
            if request.user.is_registered_with_email:
                if request.user.is_email_verified:
                    return True
                else:
                    raise PermissionDenied(detail={
                        "success": False,
                        "message": "email_not_verified",
                        "errors": [
                            {
                                "field": "token",
                                "message": "Email not verified."
                            }
                        ]
                    })
            else:
                if request.user.is_mobile_verified:
                    return True
                else:
                    raise PermissionDenied(detail={
                        "success": False,
                        "message": "mobile_not_verified",
                        "errors": [
                            {
                                "field": "token",
                                "message": "Mobile not verified."
                            }
                        ]
                    })  
        raise PermissionDenied(detail={
            "success": False,
            "message": "user_not_authenticated",
            "errors": [
                {
                    "field": "token",
                    "message": "User not authenticated."
                }
            ]
        })

class IsTncVerified(BasePermission):
    def has_permission(self, request, view):
        if request.auth and request.user.is_confirm_tnc:
            return True
        raise PermissionDenied(detail={
            "success": False,
            "message": "tnc_not_verified",
            "errors": [
                {
                    "field": "token",
                    "message": "Tnc not verified."
                }
            ]
        })

class IsRegistered(BasePermission):
    def has_permission(self, request, view):
        if request.auth and request.user.is_registered:
            return True
        raise PermissionDenied(detail={
            "success": False,
            "message": "user_not_registered",
            "errors": [
                {
                    "field": "token",
                    "message": "User not registered."
                }
            ]
        })
    

class IsSubscribed(BasePermission):
    def has_permission(self, request, view):
        if request.auth:
            if request.user.is_buyer:
                if request.user.subscription_expiry_date is not None and request.user.subscription_expiry_date >= timezone.now():
                    return True
            else:
                return True
        raise PermissionDenied(detail={
            "success": False,
            "message": "user_not_subscribed",
            "errors": [
                {
                    "field": "token",
                    "message": "User not subscribed."
                }
            ]
        })
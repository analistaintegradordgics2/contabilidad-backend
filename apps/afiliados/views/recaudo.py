from rest_framework import viewsets

class RecaudoViewSet(viewsets.ModelViewSet):
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
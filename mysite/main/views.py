from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Sponsor
from .serializers import SponsorSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone


def home(request):
    sponsors = Sponsor.objects.all().order_by('-submitted_at')
    stats = Sponsor.get_statistics()
    
    for sponsor in sponsors:
        if sponsor.custom_amount:
            sponsor.sponsorship_amount = sponsor.custom_amount
            sponsor.custom_amount = 0
            sponsor.save()

    context = {
        'sponsors': sponsors,
        **stats  # This unpacks the statistics dictionary into the context
    }
    return render(request, 'home.html', context)





@csrf_exempt
def add_sponsor(request):
    if request.method == "POST":
        name = request.POST.get("name")
        residence_location = request.POST.get("residence_location")
        primary_phone = request.POST.get("primary_phone")
        secondary_phone = request.POST.get("secondary_phone")
        sponsorship_amount = request.POST.get("sponsorship_amount")
        custom_amount = request.POST.get("custom_amount")
        payment_frequency = request.POST.get("payment_frequency")
        initial_payment_timing = request.POST.get("initial_payment_timing")
        payment_method = request.POST.get("payment_method")
        orphan_selection = request.POST.get("orphan_selection")

        # Validate required fields
        if not all([name, residence_location, primary_phone, sponsorship_amount, 
                   payment_frequency, initial_payment_timing, payment_method, orphan_selection]):
            return JsonResponse({"success": False, "error": "Missing required fields"}, status=400)

        # Create sponsor with all fields
        sponsor = Sponsor.objects.create(
            name=name,
            residence_location=residence_location,
            primary_phone=primary_phone,
            secondary_phone=secondary_phone,
            sponsorship_amount=int(sponsorship_amount),
            custom_amount=int(custom_amount) if custom_amount else None,
            payment_frequency=payment_frequency,
            initial_payment_timing=initial_payment_timing,
            payment_method=payment_method,
            orphan_selection=orphan_selection,
            submitted_at=timezone.now()
        )

        # Prepare sponsor data for response
        sponsor_data = {
            "id": sponsor.id,
            "name": sponsor.name,
            "residence_location": sponsor.get_residence_location_display(),
            "primary_phone": sponsor.primary_phone,
            "secondary_phone": sponsor.secondary_phone,
            "sponsorship_amount": sponsor.get_sponsorship_amount_display(),
            "custom_amount": sponsor.custom_amount,
            "payment_frequency": sponsor.get_payment_frequency_display(),
            "initial_payment_timing": sponsor.get_initial_payment_timing_display(),
            "payment_method": sponsor.get_payment_method_display(),
            "orphan_selection": sponsor.get_orphan_selection_display(),
            "counter": Sponsor.objects.count(),
        }

        return JsonResponse({"success": True, "sponsor": sponsor_data})
    return JsonResponse({"success": False}, status=400)



def edit_sponsor(request):
    if request.method == 'POST':
        try:
            sponsor_id = request.POST.get('id')
            sponsor = get_object_or_404(Sponsor, id=sponsor_id)
            
            sponsor.name = request.POST.get('name', sponsor.name)
            sponsor.residence_location = request.POST.get('residence_location', sponsor.residence_location)
            sponsor.primary_phone = request.POST.get('primary_phone', sponsor.primary_phone)
            sponsor.secondary_phone = request.POST.get('secondary_phone', sponsor.secondary_phone)
            sponsor.sponsorship_amount = request.POST.get('sponsorship_amount', sponsor.sponsorship_amount)
            sponsor.custom_amount = request.POST.get('custom_amount', sponsor.custom_amount)
            sponsor.payment_frequency = request.POST.get('payment_frequency', sponsor.payment_frequency)
            sponsor.initial_payment_timing = request.POST.get('initial_payment_timing', sponsor.initial_payment_timing)
            sponsor.payment_method = request.POST.get('payment_method', sponsor.payment_method)
            sponsor.orphan_selection = request.POST.get('orphan_selection', sponsor.orphan_selection)

            sponsor.save()
            
            response_data = {
                'success': True,
                'sponsor': {
                    'id': sponsor.id,
                    'name': sponsor.name,
                    'residence_location': sponsor.residence_location,
                    'primary_phone': sponsor.primary_phone,
                    'secondary_phone': sponsor.secondary_phone,
                    'sponsorship_amount': sponsor.sponsorship_amount,
                    'custom_amount': sponsor.custom_amount,
                    'payment_frequency': sponsor.payment_frequency,
                    'initial_payment_timing': sponsor.initial_payment_timing,
                    'payment_method': sponsor.payment_method,
                    'orphan_selection': sponsor.orphan_selection,

                }
            }
            return JsonResponse(response_data)

        except Exception as e:
            print(f"Error in edit_sponsor view: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)





class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

        
class SponsorViewSet(viewsets.ModelViewSet):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Add fields for filtering, searching, and ordering
    filterset_fields = ['sponsorship_amount', 'payment_frequency']
    search_fields = ['name', 'residence_location']
    ordering_fields = ['sponsorship_amount', 'submitted_at']



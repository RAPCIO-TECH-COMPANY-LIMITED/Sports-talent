from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from .models import Player, Academy
from .forms import PlayerForm, TransferForm, AcademyForm, RegisterForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

# --- PUBLIC VIEWS ---
class IndexView(TemplateView):
    template_name = 'index.html'

class SuperAdminDashboardView(LoginRequiredMixin, ListView):
    model = Academy
    template_name = 'super_admin_dashboard.html'
    context_object_name = 'academies'
    login_url = 'login'

class AcademyDetailView(LoginRequiredMixin, DetailView):
    model = Academy
    template_name = 'academy_detail.html'
    context_object_name = 'academy'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch all players linked to this specific academy
        context['players'] = self.object.players.all()
        return context

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # Log the user in automatically after successful registration
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

# --- PROTECTED VIEWS (Require Login) ---
# Notice we added LoginRequiredMixin to these views so anonymous users can't access them

class DashboardView(LoginRequiredMixin, ListView):
    model = Player
    template_name = 'dashboard.html'
    context_object_name = 'players'
    login_url = 'login'

class AcademyCreateView(LoginRequiredMixin, CreateView):
    model = Academy
    form_class = AcademyForm
    template_name = 'academy.html'
    success_url = reverse_lazy('dashboard')
    login_url = 'login'

class PlayerCreateView(LoginRequiredMixin, CreateView):
    model = Player
    form_class = PlayerForm
    template_name = 'add_player.html'
    success_url = reverse_lazy('dashboard')
    login_url = 'login'

class PlayerUpdateView(LoginRequiredMixin, UpdateView):
    model = Player
    form_class = PlayerForm
    template_name = 'add_player.html'
    success_url = reverse_lazy('dashboard')
    login_url = 'login'

class PlayerDeleteView(LoginRequiredMixin, DeleteView):
    model = Player
    template_name = 'delete_player.html'
    success_url = reverse_lazy('dashboard')
    login_url = 'login'

class PlayerTransferView(LoginRequiredMixin, UpdateView):
    model = Player
    form_class = TransferForm
    template_name = 'transfer.html'
    success_url = reverse_lazy('dashboard')
    login_url = 'login'



def contact_view(request):
    if request.method == 'POST':
        # Retrieve data from the submitted form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Format the email content
        full_message = f"New Inquiry from {first_name} {last_name} ({email})\n\nSubject: {subject}\n\nMessage:\n{message}"

        try:
            # Send the email (Make sure EMAIL_BACKEND is configured in settings.py)
            send_mail(
                subject=f"PPS Website Inquiry: {subject}",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['julietcristiana780@gmail.com'],
                fail_silently=False,
            )

            # Show a success message on the page
            messages.success(request, "Thank you! Your message has been sent successfully. Our team will get back to you shortly.")

            # Redirect to the same page to clear the form fields
            return redirect('contact')

        except Exception as e:
            # Show an error message if the email fails to send
            messages.error(request, "Oops! Something went wrong. Please try again later.")

    # Render the Canvas form for GET requests
    return render(request, 'contact.html')
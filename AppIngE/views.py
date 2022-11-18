from multiprocessing import context
from django.shortcuts import render
from .forms import *
from .models import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import redirect
# Creación de usuario


def error_403(request, exception):
    return render(request, '403.html')


def error_404(request, exception):
    return render(request, '404.html')


def error_500(request, *args, **argv):
    return render(request, '500.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            usuario = form.cleaned_data['username']
            contraseña = form.cleaned_data['password1']
            user = authenticate(username=usuario, password=contraseña)
            login(request, user)
        return redirect('perfil')
    else:
        form = UserRegisterForm()
    return render(request, "register.html", {"form": form})

# inicio de sesión


def login_request(request):

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            usuario = form.cleaned_data.get('username')
            contrasena = form.cleaned_data.get('password')
            user = authenticate(username=usuario, password=contrasena)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, "login.html", {"mensaje": "Los datos ingresados son incorrectos"})
        else:
            return render(request, "login.html", {"mensaje": "Formulario erróneo. Por favor, intentelo nuevamente."})
    else:
        form = AuthenticationForm()
        return render(request, "login.html", {'form': form})


@login_required
def logout_request(request):
    logout(request)
    return redirect('ingresar')

# Edición de perfil


@login_required
def editarPerfil(request):
    usuario = request.user
    if request.method == 'POST':
        miFormulario = UserEditForm(request.POST)
        if miFormulario.is_valid():
            usuario.email = miFormulario.cleaned_data['email']
            usuario.password1 = miFormulario.cleaned_data['password1']
            usuario.password2 = miFormulario.cleaned_data['password2']
            usuario.first_name = miFormulario.cleaned_data['first_name']
            usuario.last_name = miFormulario.cleaned_data['last_name']
            usuario.save()
            return redirect('perfil')
    else:
        miFormulario = UserEditForm(instance=usuario)
    return render(request, 'editarPerfil.html', {'miFormulario': miFormulario, 'usuario': usuario, 'imagen': getAvatar(request)})

# Perfil


@login_required
def perfil(request):
    usuario = request.user
    return render(request, 'profile.html', {'usuario': usuario, 'imagen': getAvatar(request), 'posteos': Post(request)})


def Post(request):
    posteos = Posteo.objects.filter(autor=request.user)
    if len(posteos) != 0:
        posteo = posteos
    else:
        posteo = 0
    return posteo

# Avatar


@login_required
def agregarAvatar(request):
    if request.method == 'POST':
        miFormulario = AvatarFormulario(request.POST, request.FILES)
        if miFormulario.is_valid():
            avatarViejo = Avatar.objects.filter(user=request.user)
            if (len(avatarViejo) > 0):
                avatarViejo.delete()
            avatar = Avatar(user=request.user,
                            imagen=miFormulario.cleaned_data['imagen'])
            avatar.save()
            return redirect('perfil')
    else:
        miFormulario = AvatarFormulario()
    return render(request, "agregarAvatar.html", {"miFormulario": miFormulario})


def getAvatar(request):
    avatarList = Avatar.objects.filter(user=request.user)
    if len(avatarList) != 0:
        img = avatarList[0].imagen.url
    else:
        img = 0
    return img

# About


def about(request):
    return render(request, 'about.html')

# Posteos

# Lista de Posts en el inicio.


class ListaPosts(generic.ListView):
    queryset = Posteo.objects.all().order_by('-creacion')
    template_name = 'home.html'

# Detalle Posts


class DetallePosts(generic.DetailView):
    model = Posteo
    template_name = 'DetallePosts.html'

# Crear Posteos


class CrearPosteos(LoginRequiredMixin, generic.CreateView):
    def get(self, request, *args, **kwargs):
        context = {'miFormulario': CrearPosteoForm()}
        return render(request, 'posts.html', context)

    def post(self, request, *args, **kwargs):
        miFormulario = CrearPosteoForm(request.POST, request.FILES)
        if miFormulario.is_valid():
            posteo = miFormulario.save(commit=False)
            posteo.autor = self.request.user
            slug = posteo.titulo
            posteo.slug = slug.replace(' ', '_').lower()
            posteo.save()
            return redirect(reverse_lazy('detallePost', args=[posteo.slug]))
        return render(request, 'posts.html', {'miFormulario': miFormulario})

# Actualización del post


class ActualizarPosteos(generic.UpdateView):
    model = Posteo
    fields = ['titulo', 'subtitulo', 'imagen', 'contenido']
    labels = {"titulo": "Título", "subtitulo": "Subtítulo",
              "imagen": "Imagen", "contenido": "Contenido"}
    template_name = 'actualizacionPosteo.html'


# Eliminar el post
class BorrarPosteos(generic.DeleteView):
    model = Posteo
    success_url = reverse_lazy('home')
    template_name = "borrarPosteo.html"

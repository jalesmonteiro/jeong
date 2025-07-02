from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario
from .models.perfil import PerfilUsuario

class UsuarioAdmin(BaseUserAdmin):
    # Campos que aparecem na listagem do admin
    list_display = ('email', 'nome_completo', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'nome_completo')
    ordering = ('email',)

    # Campos para edição e criação de usuário
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações pessoais', {'fields': ('nome_completo',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome_completo', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )

    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(Usuario, UsuarioAdmin)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'pontos', 'partidas_jogadas', 'vitorias')
    search_fields = ('user__email', 'user__nome_completo')
    readonly_fields = ('user',)

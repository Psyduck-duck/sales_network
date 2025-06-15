from django.contrib import admin
from django.contrib import messages
from .models import NetworkElement

@admin.action(description='Анулировать долг перед поставщиком')
def make_zero_debt(modeladmin, request, queryset):
    queryset.update(debt_to_parent=0)
    messages.success(request, 'У выбранных элементов анулирован долг')


@admin.register(NetworkElement)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('name','network_lvl', 'email', 'debt_to_parent', 'parent')
    list_display_links = ('parent', )
    # search_fields = ('city',)
    ordering = ('city',)
    actions = [make_zero_debt]

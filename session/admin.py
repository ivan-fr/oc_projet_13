from django.contrib import admin

from session.models import Thread, ChatMessage


class TabularChatMessage(admin.TabularInline):
    model = ChatMessage


class ThreadAdmin(admin.ModelAdmin):
    inlines = [TabularChatMessage]

    class Meta:
        model = Thread


admin.site.register(Thread, ThreadAdmin)

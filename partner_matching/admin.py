from django.contrib import admin
from .models import Connection

class ConnectionAdmin(admin.ModelAdmin):
    # field yang mau ditampilkan di daftar list koneksi
    list_display = ('from_user', 'to_user', 'status', 'created_at', 'updated_at')
    
    # field yang bisa dijadikan filter di sidebar kanan
    list_filter = ('status', 'created_at')
    
    # field yang bisa dicari pakai search bar
    search_fields = ('from_user__username', 'to_user__username')
    
    # mengurutkan berdasarkan tanggal dibuat (terbaru dulu)
    ordering = ('-created_at',)
    
    # membuat field tanggal jadi read-only (karena auto_now/auto_now_add)
    readonly_fields = ('created_at', 'updated_at')
    
    # pengelompokan field di halaman detail/edit 
    fieldsets = (
        (None, {
            'fields': ('from_user', 'to_user', 'status')
        }),
        ('Optional Information', {
            'fields': ('message',),
            'classes': ('collapse',) # bisa disembunyikan/ditampilkan
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Daftarkan model Connection dengan kustomisasi ConnectionAdmin
admin.site.register(Connection, ConnectionAdmin)
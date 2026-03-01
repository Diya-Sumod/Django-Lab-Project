from django.contrib import admin
from .models import Cluster, Server


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'gpu_count', 'gpu_type', 'ib_band', 'created_at']
    list_filter = ['created_at', 'gpu_type']
    search_fields = ['name', 'owner', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ['service_tag', 'server_model', 'role', 'cluster', 'idrac_ip', 'status']
    list_filter = ['status', 'cluster', 'created_at']
    search_fields = ['service_tag', 'server_model', 'cluster__name', 'role']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('cluster', 'role', 'server_model', 'generation', 'service_tag', 'status')
        }),
        ('iDRAC Information', {
            'fields': ('idrac_ip', 'idrac_username', 'idrac_password')
        }),
        ('Network Information', {
            'fields': ('bmc_mac_address', 'pxe_mac_address')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )

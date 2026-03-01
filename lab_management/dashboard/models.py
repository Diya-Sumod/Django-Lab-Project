"""
Django models for lab management dashboard.

This module defines the core data models for managing computing clusters
and their associated nodes in a laboratory environment.
"""

from django.db import models


class Cluster(models.Model):
    """Represents a computing cluster with associated nodes."""

    name = models.CharField(max_length=200)
    owner = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    gpu_count = models.IntegerField(default=0)
    gpu_type = models.CharField(max_length=100, blank=True, null=True)
    ib_band = models.CharField(max_length=100, blank=True, null=True)
    cluster_type = models.CharField(
        max_length=20,
        choices=[
            ('infra', 'Infra'),
            ('provision', 'Provision'),
            ('validation', 'Validation'),
        ],
        blank=True,
        null=True,
        help_text="Select the category for this cluster"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return string representation of cluster."""
        return str(self.name)

    class Meta:
        """Meta class for Cluster model."""
        ordering = ['name']


class Node(models.Model):
    """Represents an individual server/node within a cluster."""

    cluster = models.ForeignKey(
        Cluster,
        on_delete=models.CASCADE,
        related_name='nodes'
    )
    role = models.CharField(max_length=50)
    server_model = models.CharField(max_length=100)
    generation = models.CharField(max_length=50, blank=True)
    service_tag = models.CharField(max_length=50, unique=True)
    idrac_ip = models.GenericIPAddressField(blank=True, null=True)
    idrac_creds = models.CharField(max_length=100, blank=True)
    bmc_mac_address = models.CharField(max_length=17, blank=True)
    pxe_mac_address = models.CharField(max_length=17, blank=True)
    rack_no = models.CharField(max_length=20, blank=True)
    current_user = models.CharField(max_length=100, blank=True)
    gpu_name = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="GPU name/model"
    )
    gpu_count = models.IntegerField(
        default=0,
        help_text="Number of GPUs"
    )
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return string representation of node."""
        return f"{self.service_tag} - {self.server_model}"

    class Meta:
        """Meta class for Node model."""
        ordering = ['service_tag']


class Server(models.Model):
    """Represents a server with management and network configuration."""

    cluster = models.ForeignKey(
        Cluster,
        on_delete=models.CASCADE,
        related_name='servers'
    )
    role = models.CharField(max_length=50)
    server_model = models.CharField(max_length=100)
    generation = models.CharField(max_length=50, blank=True)
    service_tag = models.CharField(max_length=50, unique=True)
    idrac_ip = models.GenericIPAddressField(blank=True, null=True)
    idrac_creds = models.CharField(
        max_length=100,
        blank=True,
        help_text="Format: username/password"
    )
    bmc_mac_address = models.CharField(max_length=17, blank=True)
    pxe_mac_address = models.CharField(max_length=17, blank=True)
    status = models.CharField(max_length=20, default='active')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return string representation of server."""
        return f"{self.service_tag} - {self.server_model}"

    class Meta:
        """Meta class for Server model."""
        ordering = ['service_tag', 'server_model']

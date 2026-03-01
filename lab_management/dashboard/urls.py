from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('import/', views.import_excel, name='import_excel'),
    path('add-cluster/', views.add_cluster, name='add_cluster'),
    path('add-server/', views.add_server, name='add_server'),
    path('add-node-to-existing/', views.add_server_to_existing, name='add_node_to_existing'),
    path('clusters/', views.cluster_list, name='cluster_list'),
    path('nodes/', views.node_list, name='node_list'),
    path('gpus/', views.gpu_list, name='gpu_list'),
    path('cluster/<int:cluster_id>/', views.cluster_detail, name='cluster_detail'),
    path('cluster/<int:cluster_id>/edit/', views.edit_cluster, name='edit_cluster'),
    path('node/<int:node_id>/', views.node_detail, name='node_detail'),
    path('node/<int:node_id>/edit/', views.edit_node, name='edit_node'),
    path('clusters/<str:cluster_type>/', views.cluster_by_type, name='cluster_by_type'),
    path('delete-node/<int:node_id>/', views.delete_node, name='delete_node'),
    path('delete-cluster/<int:cluster_id>/', views.delete_cluster, name='delete_cluster'),
]

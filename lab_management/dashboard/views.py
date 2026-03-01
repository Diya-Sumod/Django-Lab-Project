"""
Django views for lab management dashboard.

This module contains view functions for handling HTTP requests and
rendering templates for the lab management system.
"""

# Standard library imports
import os
import tempfile

# Django imports
from django.contrib import messages
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404

# Local imports
from .models import Cluster, Node
from .utils import import_from_excel


def _filter_clusters_by_keywords(base_qs, keywords):
    """Filter clusters by keywords in name or description.

    Args:
        base_qs: Base queryset of clusters
        keywords: List of keywords to search for

    Returns:
        Filtered queryset of clusters
    """
    q = Q()
    for kw in keywords:
        q |= Q(name__icontains=kw) | Q(description__icontains=kw)
    return base_qs.filter(q) if q else base_qs.none()


def _total_nodes_for_clusters(clusters_qs):
    """Calculate total nodes for given clusters.

    Args:
        clusters_qs: Queryset of clusters

    Returns:
        Dictionary mapping cluster ID to node count
    """
    node_counts = {}
    for cluster in clusters_qs:
        node_counts[cluster.id] = cluster.nodes.count()
    return node_counts


def dashboard(request):
    """Display main dashboard with cluster statistics.

    Args:
        request: HTTP request object

    Returns:
        Rendered dashboard template
    """
    # Get all clusters
    all_clusters = Cluster.objects.all()

    # Filter clusters by type
    infra_clusters = all_clusters.filter(cluster_type='infra')
    provision_clusters = all_clusters.filter(cluster_type='provision')
    validation_clusters = all_clusters.filter(cluster_type='validation')

    # Count total nodes for each category
    infra_nodes_total = Node.objects.filter(cluster__cluster_type='infra').count()
    provision_nodes_total = Node.objects.filter(cluster__cluster_type='provision').count()
    validation_nodes_total = Node.objects.filter(cluster__cluster_type='validation').count()

    context = {
        'infra_clusters': infra_clusters,
        'provision_clusters': provision_clusters,
        'validation_clusters': validation_clusters,
        'infra_nodes_total': infra_nodes_total,
        'provision_nodes_total': provision_nodes_total,
        'validation_nodes_total': validation_nodes_total,
    }

    return render(request, 'dashboard/dashboard.html', context)


def cluster_by_type(request, cluster_type):
    """Display clusters filtered by type.

    Args:
        request: HTTP request object
        cluster_type: Type of cluster to filter

    Returns:
        Rendered cluster list template
    """
    clusters = Cluster.objects.all().prefetch_related('nodes')

    # Filter clusters by explicit type field
    if cluster_type == 'infra':
        clusters = clusters.filter(cluster_type='infra')
        title = "Infra Clusters"
    elif cluster_type == 'provision':
        clusters = clusters.filter(cluster_type='provision')
        title = "Provision Clusters"
    elif cluster_type == 'validation':
        clusters = clusters.filter(cluster_type='validation')
        title = "Validation Clusters"
    else:
        clusters = clusters.none()
        title = "Unknown Category"

    context = {
        'clusters': clusters,
        'title': title,
        'cluster_type': cluster_type,
    }

    return render(request, 'dashboard/cluster_by_type.html', context)


def import_excel(request):
    """Handle Excel file import for clusters and nodes.

    Args:
        request: HTTP request object

    Returns:
        Rendered import template or redirect after processing
    """
    if request.method == 'POST':
        if 'excel_file' not in request.FILES:
            messages.error(request, 'Please select an Excel file to upload.')
            return render(request, 'dashboard/import_excel.html')

        excel_file = request.FILES['excel_file']

        # Validate file extension
        if not excel_file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, 'Please upload a valid Excel file (.xlsx or .xls)')
            return render(request, 'dashboard/import_excel.html')

        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            for chunk in excel_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name

        try:
            # Import data
            result = import_from_excel(tmp_file_path)

            if result['success']:
                messages.success(request, f"Successfully imported {result['imported_clusters']} clusters and {result['imported_nodes']} nodes.")
                if result['errors']:
                    messages.warning(request, f"Import completed with {len(result['errors'])} warnings.")
                    for error in result['errors'][:5]:  # Show first 5 errors
                        messages.warning(request, error)
                return redirect('dashboard:dashboard')
            else:
                messages.error(request, f"Import failed: {result['error']}")

        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    return render(request, 'dashboard/import_excel.html')


def cluster_detail(request, cluster_id):
    """Display detailed information about a specific cluster.

    Args:
        request: HTTP request object
        cluster_id: ID of the cluster to display

    Returns:
        Rendered cluster detail template
    """
    cluster = get_object_or_404(Cluster, id=cluster_id)
    nodes = cluster.nodes.all()

    context = {
        'cluster': cluster,
        'nodes': nodes,
    }

    return render(request, 'dashboard/cluster_detail.html', context)


def edit_cluster(request, cluster_id):
    """Handle editing cluster information.
    
    Args:
        request: HTTP request object
        cluster_id: ID of the cluster to edit
        
    Returns:
        Rendered edit cluster template or redirect after update
    """
    cluster = get_object_or_404(Cluster, id=cluster_id)
    nodes = cluster.nodes.all()

    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            owner = request.POST.get('owner', '').strip()
            description = request.POST.get('description', '').strip()

            # Validate required fields
            if not name:
                messages.error(request, "Cluster name is required.")
                return redirect('dashboard:edit_cluster', cluster.id)

            if not owner:
                messages.error(request, "User name is required.")
                return redirect('dashboard:edit_cluster', cluster.id)

            # Update cluster with form data (cluster name, user name, and description are editable)
            cluster.name = name
            cluster.owner = owner
            cluster.description = description

            cluster.save()
            messages.success(request, f"Cluster '{cluster.name}' updated successfully.")
            return redirect('dashboard:edit_cluster', cluster.id)

        except Exception as e:
            messages.error(request, f"Error updating cluster: {str(e)}")
            return redirect('dashboard:edit_cluster', cluster.id)

    context = {
        'cluster': cluster,
        'nodes': nodes,
    }

    return render(request, 'dashboard/edit_cluster.html', context)


def node_detail(request, node_id):
    """Display detailed information about a specific node.
    
    Args:
        request: HTTP request object
        node_id: ID of the node to display
        
    Returns:
        Rendered node detail template
    """
    node = get_object_or_404(Node, id=node_id)

    context = {
        'node': node,
    }

    return render(request, 'dashboard/node_detail.html', context)


def edit_node(request, node_id):
    """Handle editing node information.
    
    Args:
        request: HTTP request object
        node_id: ID of the node to edit
        
    Returns:
        Redirect to node detail after update
    """
    node = get_object_or_404(Node, id=node_id)

    if request.method == 'POST':
        try:
            # Update node with form data
            node.service_tag = request.POST.get('service_tag', '').strip()
            node.server_model = request.POST.get('server_model', '').strip()
            node.generation = request.POST.get('generation', '').strip()
            node.role = request.POST.get('role', '').strip()
            node.idrac_ip = request.POST.get('idrac_ip', '').strip() or None
            node.idrac_creds = request.POST.get('idrac_creds', '').strip()
            node.bmc_mac_address = request.POST.get('bmc_mac_address', '').strip() or None
            node.pxe_mac_address = request.POST.get('pxe_mac_address', '').strip() or None
            node.rack_no = request.POST.get('rack_no', '').strip()
            node.current_user = request.POST.get('current_user', '').strip()
            node.gpu_name = request.POST.get('gpu_name', '').strip()
            node.gpu_count = request.POST.get('gpu_count', 0) or 0

            node.save()
            messages.success(request, f"Node '{node.service_tag}' updated successfully.")
            return redirect('dashboard:node_detail', node.id)

        except Exception as e:
            messages.error(request, f"Error updating node: {str(e)}")
            return redirect('dashboard:node_detail', node.id)

    # If GET request, redirect to node detail
    return redirect('dashboard:node_detail', node.id)


def cluster_list(request):
    """Display list of all clusters.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered cluster list template
    """
    clusters = Cluster.objects.all().prefetch_related('nodes')

    context = {
        'clusters': clusters,
    }

    return render(request, 'dashboard/cluster_list.html', context)


def node_list(request):
    """Display list of all nodes.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered node list template
    """
    nodes = Node.objects.select_related('cluster').all()

    context = {
        'nodes': nodes,
    }

    return render(request, 'dashboard/node_list.html', context)


def add_node_to_existing(request):
    nodes = Node.objects.select_related('cluster').all()

    context = {
        'nodes': nodes,
    }

    return render(request, 'dashboard/add_node_to_existing.html', context)


def gpu_list(request):
    # Get clusters that have GPUs
    gpu_clusters = Cluster.objects.filter(gpu_count__gt=0).prefetch_related('nodes')

    context = {
        'gpu_clusters': gpu_clusters,
        'total_gpus': sum(cluster.gpu_count for cluster in gpu_clusters),
    }

    return render(request, 'dashboard/gpu_list.html', context)


def add_cluster(request):
    """Handle adding new clusters and nodes.

    Args:
        request: HTTP request object

    Returns:
        Rendered add cluster template or redirect after creation
    """
    # Pre-select cluster type from URL parameter
    preselected_type = request.GET.get('type', '')
    cluster_id = request.GET.get('cluster_id', '')

    if request.method == 'POST':
        name = request.POST.get('name')
        owner = request.POST.get('owner')
        description = request.POST.get('description', '')
        cluster_type = request.POST.get('cluster_type', '')
        posted_cluster_id = request.POST.get('cluster_id', '')

        # Validate required fields (only for new cluster creation)
        if not posted_cluster_id:
            if not name or not name.strip():
                messages.error(request, "Cluster name is required.")
                return render(request, 'dashboard/add_cluster.html', {'preselected_type': request.POST.get('cluster_type', preselected_type), 'cluster_id': posted_cluster_id})

            if not owner or not owner.strip():
                messages.error(request, "User name is required.")
                return render(request, 'dashboard/add_cluster.html', {'preselected_type': request.POST.get('cluster_type', preselected_type), 'cluster_id': posted_cluster_id})

        # Collect server rows from the form
        node_count = 0
        server_rows = []
        while True:
            service_tag = request.POST.get(f'service_tag_{node_count}')
            if not service_tag:
                break
            server_rows.append({
                'service_tag': service_tag.strip(),
                'role': request.POST.get(f'role_{node_count}', ''),
                'server_model': request.POST.get(f'server_model_{node_count}', ''),
                'idrac_ip': request.POST.get(f'idrac_ip_{node_count}', ''),
                'generation': request.POST.get(f'generation_{node_count}', ''),
                'idrac_creds': request.POST.get(f'idrac_creds_{node_count}', ''),
                'bmc_mac': request.POST.get(f'bmc_mac_{node_count}', ''),
                'pxe_mac': request.POST.get(f'pxe_mac_{node_count}', ''),
                'rack_no': request.POST.get(f'rack_no_{node_count}', ''),
                'current_user': request.POST.get(f'current_user_{node_count}', ''),
                'gpu_name': request.POST.get(f'gpu_name_{node_count}', ''),
                'gpu_count': request.POST.get(f'gpu_count_{node_count}', 0) or 0,
            })
            node_count += 1

        errors = []
        seen_tags = set()
        # Check duplicates within form
        for row in server_rows:
            tag = row['service_tag']
            if not tag:
                continue
            tag_lower = tag.lower()
            if tag_lower in seen_tags:
                errors.append(f"Service tag '{tag}' is duplicated in the form. Use unique service tags.")
            else:
                seen_tags.add(tag_lower)

        # Check duplicates against existing nodes
        if seen_tags:
            tag_filters = Q()
            for tag in seen_tags:
                tag_filters |= Q(service_tag__iexact=tag)
            if tag_filters:
                existing = Node.objects.filter(tag_filters)
                if existing.exists():
                    for srv in existing:
                        errors.append(f"Service tag '{srv.service_tag}' already exists in cluster '{srv.cluster.name}' under {srv.cluster.cluster_type|title} category.")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'dashboard/add_cluster.html', {'preselected_type': request.POST.get('cluster_type', preselected_type), 'cluster_id': posted_cluster_id})

        try:
            # If cluster_id is provided, add nodes to existing cluster
            if posted_cluster_id:
                cluster = get_object_or_404(Cluster, id=posted_cluster_id)
            else:
                # Create new cluster
                cluster = Cluster.objects.create(
                    name=name,
                    owner=owner or 'System',  # Use form value or default
                    description=description,
                    cluster_type=cluster_type or preselected_type
                )

            nodes_created = 0
            for row in server_rows:
                tag = row['service_tag']
                if not tag:
                    continue
                Node.objects.create(
                    cluster=cluster,
                    role=row['role'],
                    server_model=row['server_model'] or 'Unknown',
                    generation=row['generation'],
                    service_tag=tag,
                    idrac_ip=row['idrac_ip'] if row['idrac_ip'] else None,
                    idrac_creds=row['idrac_creds'],
                    bmc_mac_address=row['bmc_mac'].strip() if row['bmc_mac'].strip() else None,
                    pxe_mac_address=row['pxe_mac'].strip() if row['pxe_mac'].strip() else None,
                    rack_no=row['rack_no'],
                    current_user=row['current_user'],
                    gpu_name=row['gpu_name'],
                    gpu_count=row['gpu_count'],
                )
                nodes_created += 1

            if posted_cluster_id:
                messages.success(request, f"Added {nodes_created} node(s) to cluster '{cluster.name}'.")
            else:
                messages.success(request, f"Cluster '{cluster.name}' created with {nodes_created} node(s).")

            # Redirect back to the cluster detail page
            return redirect('dashboard:cluster_detail', cluster.id)

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, 'dashboard/add_cluster.html', {'preselected_type': request.POST.get('cluster_type', preselected_type), 'cluster_id': posted_cluster_id})

    # If cluster_id is provided, get the cluster for context
    cluster = None
    if cluster_id:
        cluster = get_object_or_404(Cluster, id=cluster_id)

    return render(request, 'dashboard/add_cluster.html', {'preselected_type': preselected_type, 'cluster_id': cluster_id, 'cluster': cluster})


def delete_node(request, node_id):
    """Handle deleting a node from cluster.
    
    Args:
        request: HTTP request object
        node_id: ID of the node to delete
        
    Returns:
        Redirect to next URL after deletion
    """
    node = get_object_or_404(Node, id=node_id)
    cluster_name = node.cluster.name
    service_tag = node.service_tag

    # Delete the node
    try:
        node.delete()
        messages.success(request, f"Node '{service_tag}' has been removed from cluster '{cluster_name}'.")
    except Exception as e:
        messages.error(request, f"Error deleting node: {str(e)}")

    # Get the next parameter for redirect
    next_url = request.GET.get('next', 'dashboard:dashboard')
    if next_url == 'dashboard:dashboard':
        return redirect('dashboard:dashboard')
    else:
        return redirect(next_url)


def delete_cluster(request, cluster_id):
    cluster = get_object_or_404(Cluster, id=cluster_id)
    node_count = cluster.nodes.count()
    cluster_name = cluster.name

    # Delete the cluster and all its nodes (both GET and POST requests with JavaScript confirmation)
    cluster.delete()
    messages.success(request, f"Cluster '{cluster_name}' and all {node_count} nodes have been deleted.")

    # Redirect to dashboard
    return redirect('dashboard:dashboard')


def add_server_to_existing(request):
    preselected_type = request.GET.get('type', '')

    if request.method == 'POST':
        cluster_id = request.POST.get('cluster_id')
        cluster = get_object_or_404(Cluster, id=cluster_id)

        # Collect server rows from the form
        node_count = 0
        server_rows = []
        while True:
            service_tag = request.POST.get(f'service_tag_{node_count}')
            if not service_tag:
                break
            server_rows.append({
                'service_tag': service_tag.strip(),
                'role': request.POST.get(f'role_{node_count}', ''),
                'server_model': request.POST.get(f'server_model_{node_count}', ''),
                'idrac_ip': request.POST.get(f'idrac_ip_{node_count}', ''),
                'generation': request.POST.get(f'generation_{node_count}', ''),
                'idrac_creds': request.POST.get(f'idrac_creds_{node_count}', ''),
                'bmc_mac': request.POST.get(f'bmc_mac_{node_count}', ''),
                'pxe_mac': request.POST.get(f'pxe_mac_{node_count}', ''),
                'rack_no': request.POST.get(f'rack_no_{node_count}', ''),
                'current_user': request.POST.get(f'current_user_{node_count}', ''),
                'gpu_name': request.POST.get(f'gpu_name_{node_count}', ''),
                'gpu_count': request.POST.get(f'gpu_count_{node_count}', 0) or 0,
            })
            node_count += 1

        errors = []
        seen_tags = set()
        # Check duplicates within form
        for row in server_rows:
            tag = row['service_tag']
            if not tag:
                continue
            tag_lower = tag.lower()
            if tag_lower in seen_tags:
                errors.append(f"Service tag '{tag}' is duplicated in the form. Use unique service tags.")
            else:
                seen_tags.add(tag_lower)

        # Check duplicates against existing nodes
        if seen_tags:
            tag_filters = Q()
            for tag in seen_tags:
                tag_filters |= Q(service_tag__iexact=tag)
            if tag_filters:
                existing = Node.objects.filter(tag_filters)
                if existing.exists():
                    for srv in existing:
                        errors.append(f"Service tag '{srv.service_tag}' already exists in cluster '{srv.cluster.name}' under {srv.cluster.cluster_type|title} category.")

        if errors:
            for err in errors:
                messages.error(request, err)
            clusters = Cluster.objects.filter(cluster_type=preselected_type) if preselected_type else Cluster.objects.all()
            return render(request, 'dashboard/add_node_to_existing.html', {
                'preselected_type': preselected_type,
                'clusters': clusters
            })

        try:
            nodes_created = 0
            for row in server_rows:
                tag = row['service_tag']
                if not tag:
                    continue
                Node.objects.create(
                    cluster=cluster,
                    role=row['role'],
                    server_model=row['server_model'] or 'Unknown',
                    generation=row['generation'],
                    service_tag=tag,
                    idrac_ip=row['idrac_ip'] if row['idrac_ip'] else None,
                    idrac_creds=row['idrac_creds'],
                    bmc_mac_address=row['bmc_mac'].strip() if row['bmc_mac'].strip() else None,
                    pxe_mac_address=row['pxe_mac'].strip() if row['pxe_mac'].strip() else None,
                    rack_no=row['rack_no'],
                    current_user=row['current_user'],
                    gpu_name=row['gpu_name'],
                    gpu_count=row['gpu_count'],
                )
                nodes_created += 1

            messages.success(request, f"Added {nodes_created} node(s) to cluster '{cluster.name}'.")
            return redirect('dashboard:cluster_detail', cluster.id)

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            clusters = Cluster.objects.filter(cluster_type=preselected_type) if preselected_type else Cluster.objects.all()
            return render(request, 'dashboard/add_node_to_existing.html', {
                'preselected_type': preselected_type,
                'clusters': clusters
            })

    # GET request - show form
    clusters = Cluster.objects.filter(cluster_type=preselected_type) if preselected_type else Cluster.objects.all()
    return render(request, 'dashboard/add_node_to_existing.html', {
        'preselected_type': preselected_type,
        'clusters': clusters
    })


def add_server(request):
    clusters = Cluster.objects.all()

    if request.method == 'POST':
        cluster_id = request.POST.get('cluster_id')

        try:
            cluster = Cluster.objects.get(id=cluster_id)

            # Add nodes from form data
            nodes_created = 0
            node_count = 0

            # Find all node data from form
            while True:
                service_tag = request.POST.get(f'service_tag_{node_count}')
                if not service_tag:
                    break

                role = request.POST.get(f'role_{node_count}', '')
                server_model = request.POST.get(f'server_model_{node_count}', '')
                idrac_ip = request.POST.get(f'idrac_ip_{node_count}', '')
                generation = request.POST.get(f'generation_{node_count}', '')
                idrac_creds = request.POST.get(f'idrac_creds_{node_count}', '')
                bmc_mac = request.POST.get(f'bmc_mac_{node_count}', '')
                pxe_mac = request.POST.get(f'pxe_mac_{node_count}', '')
                rack_no = request.POST.get(f'rack_no_{node_count}', '')
                current_user = request.POST.get(f'current_user_{node_count}', '')
                gpu_name = request.POST.get(f'gpu_name_{node_count}', '')
                gpu_count = request.POST.get(f'gpu_count_{node_count}', 0) or 0

                if service_tag.strip():  # Only create if service tag is provided
                    service_tag_clean = service_tag.strip()

                    # Check if node with this service tag already exists in any cluster
                    existing_node = Node.objects.filter(service_tag__iexact=service_tag_clean).first()
                    if existing_node:
                        messages.error(request, f"Node with service tag '{service_tag_clean}' already exists in cluster '{existing_node.cluster.name}'. Delete it from there first before adding to another cluster.")
                    else:
                        Node.objects.create(
                            cluster=cluster,
                            role=role,
                            server_model=server_model or 'Unknown',
                            generation=generation,
                            service_tag=service_tag_clean,
                            idrac_ip=idrac_ip if idrac_ip else None,
                            idrac_creds=idrac_creds,
                            bmc_mac_address=bmc_mac.strip() if bmc_mac.strip() else None,
                            pxe_mac_address=pxe_mac.strip() if pxe_mac.strip() else None,
                            rack_no=rack_no,
                            current_user=current_user,
                            gpu_name=gpu_name,
                            gpu_count=gpu_count,
                            status='active'
                        )
                        nodes_created += 1

                node_count += 1

            if nodes_created > 0:
                messages.success(request, f"Added {nodes_created} nodes to cluster '{cluster.name}'.")
            else:
                messages.success(request, f"No nodes added to cluster '{cluster.name}'.")

            return redirect('dashboard:dashboard')

        except Cluster.DoesNotExist:
            messages.error(request, "Cluster not found.")
        except Exception as e:
            messages.error(request, f"Error adding nodes: {str(e)}")

    context = {
        'clusters': clusters,
    }

    return render(request, 'dashboard/add_node_to_existing.html', context)

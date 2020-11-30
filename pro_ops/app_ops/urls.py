from django.urls import include,path,re_path
from django.conf import settings
from django.conf.urls.static import static
from . import (
    views,
    server_views,
    dml_views,
    os_views,
    user_views,
    doc_views,
    cmanage_views,
)

urlpatterns = [
    path('', views.main),
    path('login/',views.login_in),
    path('logout/',views.login_out),
    path('main/',views.main),
    path('doc/create_project/',doc_views.create_project),
    path('doc/create_dir/',doc_views.create_dir),
    path('doc/list_dir/',doc_views.list_dir),
    path('doc/rename/',doc_views.rename),
    path('doc/delete/',doc_views.del_dir_or_file),
    path('doc/update_group/',doc_views.update_group),
    path('doc/update_perm/',doc_views.update_perm),
    path('doc/get_perms/',doc_views.get_perms),
    path('cmanage/',cmanage_views.cmanage_list),
    path('cmanage/add_order/',cmanage_views.add_order),
    path('user_manager/',user_views.user_list),
    path('server/',server_views.get_list),
    path('server/export/',server_views.export_excel),
    path('os/',os_views.get_list),
    path('os/export/',os_views.export_excel),
    path('dml/',dml_views.dml),
    path('doc/perms/',doc_views.perms),
    re_path(r'^doc/add_or_edit/([0-9]*)',doc_views.add_or_edit),
     re_path(r'^doc/add_or_edit_group/([0-9]*)',doc_views.add_or_edit_group),
    re_path(r'^doc/([0-9]*)',doc_views.doc),
    re_path(r'^os/add_or_edit_os/([0-9]*)',os_views.add_or_edit),
    re_path(r'^server/add_or_edit_server/([0-9]*)',server_views.add_or_edit),
    re_path(r'^user_detail/([0-9]*)',user_views.user_detail),
    re_path(r'^change_pd_or_perm/([0-9]*)',user_views.change_pd_or_perm),
    re_path(r'^del_user/([0-9]*)',user_views.del_user),
] + static(settings.STATIC_URL,document_root = settings.STATIC_ROOT)

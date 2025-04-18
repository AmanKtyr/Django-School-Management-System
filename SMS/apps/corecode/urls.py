from django.urls import path
from . import views
from .views import (
    ClassCreateView,
    ClassDeleteView,
    ClassListView,
    ClassUpdateView,
    CurrentSessionAndTermView,
    IndexView,
    SessionCreateView,
    SessionDeleteView,
    SessionListView,
    SessionUpdateView,
    SubjectCreateView,
    SubjectDeleteView,
    SubjectListView,
    SubjectUpdateView,
    TermCreateView,
    TermDeleteView,
    TermListView,
    TermUpdateView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("site-config", views.site_config_view, name="configs"),  # Corrected view
    path(
        "current-session/", CurrentSessionAndTermView.as_view(), name="current-session"
    ),
    path("session/list/", SessionListView.as_view(), name="sessions"),
    path("session/create/", SessionCreateView.as_view(), name="session-create"),
    path(
        "session/<int:pk>/update/",
        SessionUpdateView.as_view(),
        name="session-update",
    ),
    path(
        "session/<int:pk>/delete/",
        SessionDeleteView.as_view(),
        name="session-delete",
    ),
    path("term/list/", TermListView.as_view(), name="terms"),
    path("term/create/", TermCreateView.as_view(), name="term-create"),
    path("term/<int:pk>/update/", TermUpdateView.as_view(), name="term-update"),
    path("term/<int:pk>/delete/", TermDeleteView.as_view(), name="term-delete"),
    path("class/list/", ClassListView.as_view(), name="classes"),
    path("class/create/", ClassCreateView.as_view(), name="class-create"),
    path("class/<int:pk>/update/", ClassUpdateView.as_view(), name="class-update"),
    path("class/<int:pk>/delete/", ClassDeleteView.as_view(), name="class-delete"),
    path("subject/list/", SubjectListView.as_view(), name="subjects"),
    path("subject/create/", SubjectCreateView.as_view(), name="subject-create"),
    path(
        "subject/<int:pk>/update/",
        SubjectUpdateView.as_view(),
        name="subject-update",
    ),
    path(
        "subject/<int:pk>/delete/",
        SubjectDeleteView.as_view(),
        name="subject-delete",
    ),
    path('siteconfig/', views.site_config_view, name='siteconfig'),
    path("college-profile/", views.college_profile_view, name="college-profile"),
    path('site-config/', views.site_config_view, name='site_config'),
    path('college-profile/', views.college_profile_view, name='college_profile'),
    path("fees/settings/", views.fee_settings, name="fee_settings"),
    path('api/get-fee-settings/<int:class_id>/<str:section>/', views.get_fee_settings, name='get_fee_settings'),
    path('fees/settings/list/', views.fee_settings_list, name='fee_settings_list'),
    path('api/get-sections/<int:class_id>/', views.get_sections_by_class, name='get_sections_by_class'),
    path('logout/', views.custom_logout_view, name='logout'),

    # System Settings URLs
    path('system-settings/', views.system_settings_dashboard, name='system_settings_dashboard'),
    path('system-settings/general/', views.general_settings, name='general_settings'),
    path('system-settings/academic/', views.academic_settings, name='academic_settings'),
    path('system-settings/database/', views.database_management, name='database_management'),
    path('system-settings/backup-restore/', views.backup_restore, name='backup_restore'),
    path('system-settings/user-permissions/', views.user_permissions, name='user_permissions'),
    path('system-settings/security-logs/', views.security_logs, name='security_logs'),
]

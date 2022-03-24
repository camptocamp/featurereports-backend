ARG GEORCHESTRA_VERSION

FROM georchestra/ldap:${GEORCHESTRA_VERSION}

COPY add_role /docker-entrypoint.d/99-add_roles
COPY role_report_admin.ldif /

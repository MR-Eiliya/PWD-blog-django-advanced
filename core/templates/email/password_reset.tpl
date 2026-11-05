{% extends "mail_templated/base.tpl" %}

{% block subject %}
Password Reset
{% endblock %}

{% block body %}
This is a plain text part.
{% endblock %}

{% block html %}
http://127.0.0.1:8020/accounts/api/v1/password-reset/confirm/{{token}}/

{% endblock %}
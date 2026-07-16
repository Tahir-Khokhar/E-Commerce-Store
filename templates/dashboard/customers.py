{% extends 'base.html' %}
{% block title %}Customers{% endblock %}
{% block content %}
<h2 class="mb-3">Customers</h2>
<table class="table table-striped">
    <thead><tr><th>Email</th><th>Name</th><th>Joined</th><th>Verified</th></tr></thead>
    <tbody>
        {% for c in customers %}
        <tr><td>{{ c.email }}</td><td>{{ c.full_name }}</td><td>{{ c.date_joined|date }}</td><td>{% if c.is_verified %}Yes{% else %}No{% endif %}</td></tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}

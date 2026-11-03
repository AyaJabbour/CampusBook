def test_rooms_list_active_only_for_guests(client, sample_room, inactive_room):
    """Vérifie que seules les salles actives sont visibles pour les visiteurs."""
    response = client.get('/rooms/')
    assert response.status_code == 200
    assert sample_room.name.encode('utf-8') in response.data
    assert inactive_room.name.encode('utf-8') not in response.data


def test_rooms_search_by_name(client, sample_room, sample_room_2):
    """Vérifie la recherche d'une salle par nom."""
    response = client.get('/rooms/?search=Turing')
    assert response.status_code == 200
    assert sample_room.name.encode('utf-8') in response.data
    assert sample_room_2.name.encode('utf-8') not in response.data


def test_rooms_filter_by_building(client, sample_room):
    """Vérifie le filtrage des salles par bâtiment."""
    response = client.get(f'/rooms/?building={sample_room.building}')
    assert response.status_code == 200
    assert sample_room.name.encode('utf-8') in response.data


def test_rooms_filter_by_min_capacity(client, sample_room, sample_room_2):
    """Vérifie le filtrage par capacité minimale."""
    # sample_room: 20 places, sample_room_2: 30 places
    response = client.get('/rooms/?min_capacity=25')
    assert response.status_code == 200
    assert sample_room_2.name.encode('utf-8') in response.data
    assert sample_room.name.encode('utf-8') not in response.data


def test_rooms_filter_by_equipment(client, sample_room, sample_room_2):
    """Vérifie le filtrage par équipement spécifique."""
    # sample_room has 'Tableau blanc', sample_room_2 does not
    response = client.get('/rooms/?equipment=Tableau')
    assert response.status_code == 200
    assert sample_room.name.encode('utf-8') in response.data
    assert sample_room_2.name.encode('utf-8') not in response.data


def test_room_detail_view(client, sample_room):
    """Vérifie l'accès à la fiche détaillée d'une salle."""
    response = client.get(f'/rooms/{sample_room.id}')
    assert response.status_code == 200
    assert sample_room.name.encode('utf-8') in response.data
    assert sample_room.building.encode('utf-8') in response.data


def test_inactive_room_hidden_from_public(client, inactive_room):
    """Vérifie qu'un visiteur ne peut pas accéder aux détails d'une salle inactive (404)."""
    response = client.get(f'/rooms/{inactive_room.id}')
    assert response.status_code == 404

import pytest
import uuid
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_view_user_cannot_edit_board(client: AsyncClient):
    """Тест: пользователь с правами view не может редактировать доску."""
    # Создаем владельца и пользователя
    owner_login = f"owner_view_{uuid.uuid4().hex[:8]}@example.com"
    viewer_login = f"viewer_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": viewer_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    viewer_token = (await client.post("/api/v1/auth/login", json={"login": viewer_login, "password": password})).json()["token"]
    
    # Создаем доску и даем view доступ
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"View Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": viewer_login, "permission": "view"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Пытаемся редактировать доску с правами view
    response = await client.put(
        f"/api/v1/boards/{board_id}",
        json={"title": "Hacked Title"},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_view_user_cannot_create_sticker(client: AsyncClient):
    """Тест: пользователь с правами view не может создавать стикеры."""
    owner_login = f"owner_sticker_{uuid.uuid4().hex[:8]}@example.com"
    viewer_login = f"viewer_sticker_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": viewer_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    viewer_token = (await client.post("/api/v1/auth/login", json={"login": viewer_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Sticker Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": viewer_login, "permission": "view"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Пытаемся создать стикер с правами view
    response = await client.post(
        f"/api/v1/boards/{board_id}/stickers",
        json={"x": 100, "y": 200},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_view_user_cannot_update_sticker(client: AsyncClient):
    """Тест: пользователь с правами view не может обновлять стикеры."""
    owner_login = f"owner_update_{uuid.uuid4().hex[:8]}@example.com"
    viewer_login = f"viewer_update_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": viewer_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    viewer_token = (await client.post("/api/v1/auth/login", json={"login": viewer_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Update Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    sticker_id = (await client.post(
        f"/api/v1/boards/{board_id}/stickers",
        json={"x": 100, "y": 200, "text": "Original"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["stickerId"]
    
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": viewer_login, "permission": "view"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Пытаемся обновить стикер с правами view
    response = await client.patch(
        f"/api/v1/boards/{board_id}/stickers/{sticker_id}",
        json={"text": "Hacked"},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_view_user_cannot_delete_sticker(client: AsyncClient):
    """Тест: пользователь с правами view не может удалять стикеры."""
    owner_login = f"owner_delete_{uuid.uuid4().hex[:8]}@example.com"
    viewer_login = f"viewer_delete_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": viewer_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    viewer_token = (await client.post("/api/v1/auth/login", json={"login": viewer_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Delete Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    sticker_id = (await client.post(
        f"/api/v1/boards/{board_id}/stickers",
        json={"x": 100, "y": 200},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["stickerId"]
    
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": viewer_login, "permission": "view"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Пытаемся удалить стикер с правами view
    response = await client.delete(
        f"/api/v1/boards/{board_id}/stickers/{sticker_id}",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_edit_user_can_edit_board(client: AsyncClient):
    """Тест: пользователь с правами edit может редактировать доску."""
    owner_login = f"owner_edit_{uuid.uuid4().hex[:8]}@example.com"
    editor_login = f"editor_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": editor_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    editor_token = (await client.post("/api/v1/auth/login", json={"login": editor_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Edit Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": editor_login, "permission": "edit"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Редактируем доску с правами edit
    new_title = f"Edited {uuid.uuid4().hex[:8]}"
    response = await client.put(
        f"/api/v1/boards/{board_id}",
        json={"title": new_title},
        headers={"Authorization": f"Bearer {editor_token}"},
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == new_title


@pytest.mark.asyncio
async def test_edit_user_can_create_sticker(client: AsyncClient):
    """Тест: пользователь с правами edit может создавать стикеры."""
    owner_login = f"owner_create_{uuid.uuid4().hex[:8]}@example.com"
    editor_login = f"editor_create_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": editor_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    editor_token = (await client.post("/api/v1/auth/login", json={"login": editor_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Create Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": editor_login, "permission": "edit"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Создаем стикер с правами edit
    response = await client.post(
        f"/api/v1/boards/{board_id}/stickers",
        json={"x": 100, "y": 200, "text": f"Editor Sticker {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {editor_token}"},
    )
    
    assert response.status_code == 201
    assert response.json()["boardId"] == board_id


@pytest.mark.asyncio
async def test_edit_user_cannot_delete_board(client: AsyncClient):
    """Тест: пользователь с правами edit не может удалять доску."""
    owner_login = f"owner_del_{uuid.uuid4().hex[:8]}@example.com"
    editor_login = f"editor_del_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": editor_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    editor_token = (await client.post("/api/v1/auth/login", json={"login": editor_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Delete Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": editor_login, "permission": "edit"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Пытаемся удалить доску с правами edit
    response = await client.delete(
        f"/api/v1/boards/{board_id}",
        headers={"Authorization": f"Bearer {editor_token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_edit_user_cannot_share_board(client: AsyncClient):
    """Тест: пользователь с правами edit не может предоставлять доступ."""
    owner_login = f"owner_share_{uuid.uuid4().hex[:8]}@example.com"
    editor_login = f"editor_share_{uuid.uuid4().hex[:8]}@example.com"
    third_user_login = f"third_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": editor_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": third_user_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    editor_token = (await client.post("/api/v1/auth/login", json={"login": editor_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Share Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": editor_login, "permission": "edit"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Пытаемся предоставить доступ с правами edit
    response = await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": third_user_login, "permission": "view"},
        headers={"Authorization": f"Bearer {editor_token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_edit_user_cannot_revoke_share(client: AsyncClient):
    """Тест: пользователь с правами edit не может отзывать доступ."""
    owner_login = f"owner_revoke_{uuid.uuid4().hex[:8]}@example.com"
    editor_login = f"editor_revoke_{uuid.uuid4().hex[:8]}@example.com"
    viewer_login = f"viewer_revoke_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": editor_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": viewer_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    editor_token = (await client.post("/api/v1/auth/login", json={"login": editor_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Revoke Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": editor_login, "permission": "edit"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": viewer_login, "permission": "view"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Пытаемся отозвать доступ с правами edit
    import json
    response = await client.request(
        "DELETE",
        f"/api/v1/boards/{board_id}/share",
        content=json.dumps({"userLogin": viewer_login}),
        headers={"Authorization": f"Bearer {editor_token}", "Content-Type": "application/json"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_no_access_user_cannot_get_board(client: AsyncClient):
    """Тест: пользователь без доступа не может получить доску."""
    owner_login = f"owner_noaccess_{uuid.uuid4().hex[:8]}@example.com"
    stranger_login = f"stranger_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": stranger_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    stranger_token = (await client.post("/api/v1/auth/login", json={"login": stranger_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"No Access Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    # Пытаемся получить доску без доступа
    response = await client.get(
        f"/api/v1/boards/{board_id}",
        headers={"Authorization": f"Bearer {stranger_token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_permission_from_view_to_edit(client: AsyncClient):
    """Тест: обновление прав доступа с view на edit."""
    owner_login = f"owner_updateperm_{uuid.uuid4().hex[:8]}@example.com"
    user_login = f"user_updateperm_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": user_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    user_token = (await client.post("/api/v1/auth/login", json={"login": user_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Update Perm Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    # Даем view доступ
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": user_login, "permission": "view"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Проверяем, что не может редактировать
    response = await client.put(
        f"/api/v1/boards/{board_id}",
        json={"title": "Hacked"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    
    # Обновляем права на edit
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": user_login, "permission": "edit"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Теперь может редактировать
    response = await client.put(
        f"/api/v1/boards/{board_id}",
        json={"title": f"Updated {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_cannot_share_to_self(client: AsyncClient):
    """Тест: нельзя предоставить доступ самому себе."""
    owner_login = f"owner_self_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Self Share Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    # Пытаемся предоставить доступ самому себе
    response = await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": owner_login, "permission": "edit"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_cannot_revoke_owner_access(client: AsyncClient):
    """Тест: нельзя отозвать доступ у владельца."""
    owner_login = f"owner_revoke_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Revoke Owner Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    # Пытаемся отозвать доступ у владельца
    import json
    response = await client.request(
        "DELETE",
        f"/api/v1/boards/{board_id}/share",
        content=json.dumps({"userLogin": owner_login}),
        headers={"Authorization": f"Bearer {owner_token}", "Content-Type": "application/json"},
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_edit_user_can_update_own_sticker(client: AsyncClient):
    """Тест: пользователь с правами edit может обновлять свои стикеры."""
    owner_login = f"owner_own_{uuid.uuid4().hex[:8]}@example.com"
    editor_login = f"editor_own_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": editor_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    editor_token = (await client.post("/api/v1/auth/login", json={"login": editor_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Own Sticker Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": editor_login, "permission": "edit"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Создаем стикер от имени editor
    sticker_id = (await client.post(
        f"/api/v1/boards/{board_id}/stickers",
        json={"x": 100, "y": 200, "text": "Original"},
        headers={"Authorization": f"Bearer {editor_token}"},
    )).json()["stickerId"]
    
    # Обновляем свой стикер
    new_text = f"Updated {uuid.uuid4().hex[:8]}"
    response = await client.patch(
        f"/api/v1/boards/{board_id}/stickers/{sticker_id}",
        json={"text": new_text},
        headers={"Authorization": f"Bearer {editor_token}"},
    )
    
    assert response.status_code == 200
    assert response.json()["text"] == new_text


@pytest.mark.asyncio
async def test_edit_user_can_delete_own_sticker(client: AsyncClient):
    """Тест: пользователь с правами edit может удалять свои стикеры."""
    owner_login = f"owner_delown_{uuid.uuid4().hex[:8]}@example.com"
    editor_login = f"editor_delown_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": editor_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    editor_token = (await client.post("/api/v1/auth/login", json={"login": editor_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Del Own Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": editor_login, "permission": "edit"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Создаем стикер от имени editor
    sticker_id = (await client.post(
        f"/api/v1/boards/{board_id}/stickers",
        json={"x": 100, "y": 200},
        headers={"Authorization": f"Bearer {editor_token}"},
    )).json()["stickerId"]
    
    # Удаляем свой стикер
    response = await client.delete(
        f"/api/v1/boards/{board_id}/stickers/{sticker_id}",
        headers={"Authorization": f"Bearer {editor_token}"},
    )
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_edit_user_can_update_owner_sticker(client: AsyncClient):
    """Тест: пользователь с правами edit может обновлять стикеры владельца."""
    owner_login = f"owner_ownerst_{uuid.uuid4().hex[:8]}@example.com"
    editor_login = f"editor_ownerst_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": editor_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    editor_token = (await client.post("/api/v1/auth/login", json={"login": editor_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Owner Sticker Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    # Создаем стикер от имени owner
    sticker_id = (await client.post(
        f"/api/v1/boards/{board_id}/stickers",
        json={"x": 100, "y": 200, "text": "Owner's Sticker"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["stickerId"]
    
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": editor_login, "permission": "edit"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Editor обновляет стикер owner
    new_text = f"Edited by Editor {uuid.uuid4().hex[:8]}"
    response = await client.patch(
        f"/api/v1/boards/{board_id}/stickers/{sticker_id}",
        json={"text": new_text},
        headers={"Authorization": f"Bearer {editor_token}"},
    )
    
    assert response.status_code == 200
    assert response.json()["text"] == new_text


@pytest.mark.asyncio
async def test_edit_user_can_delete_owner_sticker(client: AsyncClient):
    """Тест: пользователь с правами edit может удалять стикеры владельца."""
    owner_login = f"owner_delowner_{uuid.uuid4().hex[:8]}@example.com"
    editor_login = f"editor_delowner_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": editor_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    editor_token = (await client.post("/api/v1/auth/login", json={"login": editor_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Del Owner Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    # Создаем стикер от имени owner
    sticker_id = (await client.post(
        f"/api/v1/boards/{board_id}/stickers",
        json={"x": 100, "y": 200},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["stickerId"]
    
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": editor_login, "permission": "edit"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Editor удаляет стикер owner
    response = await client.delete(
        f"/api/v1/boards/{board_id}/stickers/{sticker_id}",
        headers={"Authorization": f"Bearer {editor_token}"},
    )
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_view_user_can_get_board(client: AsyncClient):
    """Тест: пользователь с правами view может получить доску."""
    owner_login = f"owner_get_{uuid.uuid4().hex[:8]}@example.com"
    viewer_login = f"viewer_get_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": viewer_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    viewer_token = (await client.post("/api/v1/auth/login", json={"login": viewer_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"Get Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": viewer_login, "permission": "view"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Получаем доску с правами view
    response = await client.get(
        f"/api/v1/boards/{board_id}",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    
    assert response.status_code == 200
    assert response.json()["boardId"] == board_id


@pytest.mark.asyncio
async def test_view_user_can_list_boards(client: AsyncClient):
    """Тест: пользователь с правами view видит доску в списке."""
    owner_login = f"owner_list_{uuid.uuid4().hex[:8]}@example.com"
    viewer_login = f"viewer_list_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post("/api/v1/auth/register", json={"login": owner_login, "password": password})
    await client.post("/api/v1/auth/register", json={"login": viewer_login, "password": password})
    
    owner_token = (await client.post("/api/v1/auth/login", json={"login": owner_login, "password": password})).json()["token"]
    viewer_token = (await client.post("/api/v1/auth/login", json={"login": viewer_login, "password": password})).json()["token"]
    
    board_id = (await client.post(
        "/api/v1/boards/",
        json={"title": f"List Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )).json()["boardId"]
    
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": viewer_login, "permission": "view"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    
    # Получаем список досок с правами view
    response = await client.get(
        "/api/v1/boards/?filter=all",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    
    assert response.status_code == 200
    boards = response.json()["boards"]
    board_ids = [b["boardId"] for b in boards]
    assert board_id in board_ids




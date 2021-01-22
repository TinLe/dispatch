from fastapi.encoders import jsonable_encoder
from typing import Optional

from dispatch.search import service as search_service

from .models import Notification, NotificationCreate, NotificationUpdate


def get(*, db_session, notification_id: int) -> Optional[Notification]:
    """Gets a notifcation by id."""
    return db_session.query(Notification).filter(Notification.id == notification_id).one_or_none()


def get_all(*, db_session):
    """Gets all notifications."""
    return db_session.query(Notification)


def create(*, db_session, notification_in: NotificationCreate) -> Notification:
    """Creates a new notification."""
    filters = [
        search_service.get(db_session=db_session, search_filter_id=f.id)
        for f in notification_in.filters
    ]

    notification = Notification(
        **notification_in.dict(exclude={"filters"}),
        filters=filters,
    )

    db_session.add(notification)
    db_session.commit()
    return notification


def update(
    *, db_session, notification: Notification, notification_in: NotificationUpdate
) -> Notification:
    """Updates a notification."""
    notification_data = jsonable_encoder(notification)

    filters = [
        search_service.get(db_session=db_session, search_filter_id=f.id)
        for f in notification_in.filters
    ]

    update_data = notification_in.dict(
        skip_defaults=True,
        exclude={"filters"},
    )

    for field in notification_data:
        if field in update_data:
            setattr(notification, field, update_data[field])

    notification.filters = filters
    db_session.add(notification)
    db_session.commit()
    return notification


def delete(*, db_session, notification_id: int):
    """Deletes a notification."""
    notification = (
        db_session.query(Notification).filter(Notification.id == notification_id).one_or_none()
    )
    db_session.delete(notification)
    db_session.commit()

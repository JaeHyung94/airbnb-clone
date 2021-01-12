from django.shortcuts import render, redirect, reverse
from rooms import models as room_models
from . import models as list_models

# Create your views here.
def save_room(request, room_pk):
    room = room_models.Room.objects.get_or_none(pk=room_pk)

    if room is not None:
        the_list, created = list_models.List.objects.get_or_create(
            user=request.user, name="My Favourite Houses"
        )

        the_list.rooms.add(room)

    return redirect(reverse("rooms:detail", kwargs={"pk": room_pk}))

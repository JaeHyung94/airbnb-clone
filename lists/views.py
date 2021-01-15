from django.shortcuts import render, redirect, reverse
from django.views.generic.base import TemplateView
from rooms import models as room_models
from . import models as list_models

# Create your views here.
def toggle_room(request, room_pk):
    action = request.GET.get("action", None)

    room = room_models.Room.objects.get_or_none(pk=room_pk)

    if room is not None and action is not None:
        the_list, created = list_models.List.objects.get_or_create(
            user=request.user, name="My Favourite Houses"
        )

        if action == "add":
            the_list.rooms.add(room)
        else:
            the_list.rooms.remove(room)

        return redirect(reverse("rooms:detail", kwargs={"pk": room_pk}))


class FavListView(TemplateView):

    template_name = "lists/list_detail.html"

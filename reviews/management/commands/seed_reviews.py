import random
from django_seed import Seed
from django.core.management.base import BaseCommand
from reviews import models as review_models
from users import models as user_models
from rooms import models as room_models

class Command(BaseCommand):
    help = 'This command makes reviews'

    def add_arguments(self, parser):
        parser.add_argument("--number", default=1, type=int, help = 'How many reviews do you want to make?')

    def handle(self, *args, **options):
        
        number = options.get('number', 1)

        seeder = Seed.seeder()

        users = user_models.User.objects.all()
        rooms = room_models.Room.objects.all()

        seeder.add_entity(
            review_models.Review,
            number,
            {
                "review": lambda x: seeder.faker.sentence(),
                "accuracy": lambda x: random.randint(1, 5),
                "communication": lambda x: random.randint(1, 5),
                "cleanliness": lambda x: random.randint(1, 5),
                "location": lambda x: random.randint(1, 5),
                "check_in": lambda x: random.randint(1, 5),
                "value": lambda x: random.randint(1, 5),
                "user": lambda x: random.choice(users),
                "room": lambda x: random.choice(rooms),
            }
        )

        seeder.execute()

        self.stdout.write(self.style.SUCCESS(f"{number} Reviews created"))
        
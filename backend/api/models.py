from django.db import models
import uuid


class Item(models.Model):
    id = models.AutoField(primary_key=True)
    item_id = models.IntegerField()
    item_type = models.CharField(max_length=100)
    guid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f'{self.item_id} {self.item_type}'

    @classmethod
    def get_item_id_by_guid(cls, guid):
        try:
            item = cls.objects.get(guid=guid)
            return item.item_id
        except cls.DoesNotExist:
            return None

    @classmethod
    def check_or_create_item(cls, item_id, item_type):
        try:
            item = cls.objects.get(item_id=item_id, item_type=item_type)
        except cls.DoesNotExist:
            item = cls(item_id=item_id, item_type=item_type)
            item.save()

        return item

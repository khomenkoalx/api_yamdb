import os
import pandas as pd
from django.core.management import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = """Import of CSV data and creation/updating of model objects.
    This command takes only one CSV file and model name at a time."""

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Path to CSV file')
        parser.add_argument('--model', type=str, help='Model name to import')

    def handle(self, *args, **kwargs):
        file_path = kwargs.get('path')
        model_name = kwargs.get('model')

        if not file_path or not model_name:
            self.stdout.write(
                self.style.ERROR('Необходимо указать путь (--path) и модель (--model)')
            )
            return

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Файл {file_path} не найден'))
            return

        file_df = self.read_csv(file_path)
        if file_df is None:
            return

        if model_name == 'GenreTitle':
            self.process_mtm_table(file_df, model_name)
            return

        model = self.get_model(model_name)
        if not model:
            return

        for _, row in file_df.iterrows():
            data = self.process_row(row, model)
            if data:
                self.save_model_object(data, model)

    def get_model(self, model_name):
        """Get the model from the app."""
        try:
            if model_name == 'User':
                return apps.get_model('users', 'User')
            else:
                return apps.get_model('reviews', model_name)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Модель {model_name} не удалось найти. Ошибка: {e}'
                )
            )
            return None

    def read_csv(self, file_path):
        """Read the CSV file."""
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Ошибка при чтении файла: {e}'
                )
            )
            return None
    def process_mtm_table(self, file_df, model_name):
        """Handle MTM relationships by populating the through table."""
        if model_name == 'GenreTitle':
            title_model = apps.get_model('reviews', 'Title')
            genre_model = apps.get_model('reviews', 'Genre')
            for _, row in file_df.iterrows():
                try:
                    title = title_model.objects.get(id=row['title_id'])
                    genre = genre_model.objects.get(id=row['genre_id'])
                    title.genre.add(genre)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Связь добавлена: Title {title.id} - Genre {genre.id}'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Ошибка: {e}')
                    )

    def process_row(self, row, model):
        """Process a single row of CSV data and return the model data."""
        data = {}
        for field in model._meta.fields:
            field_name = field.name

            if field.is_relation:
                data[field_name] = self.get_related_object(
                    field, field_name, row
                )
            elif field_name in row:
                data[field_name] = row[field_name]

        return data if data else None

    def get_related_object(self, field, field_name, row):
        """Handle related fields, considering _id suffix and field name."""
        related_field_name = f'{field_name}_id'

        if related_field_name in row:
            return field.related_model.objects.get(id=row[related_field_name])
        elif field_name in row:
            return field.related_model.objects.get(id=row[field_name])

        return None

    def save_model_object(self, data, model):
        """Save or update the model object."""
        try:
            obj, created = model.objects.update_or_create(**data)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Создан объект {model.__name__}: {obj}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Обновлен объект {model.__name__}: {obj}'
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Ошибка при сохранении объекта {model.__name__}: {e}'
                )
            )

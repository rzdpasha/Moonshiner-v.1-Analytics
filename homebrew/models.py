from datetime import datetime
from django.db import models
from django.db.models import CheckConstraint, Q, F
from django.utils import timezone

# ############################################################################
########## BREW ##############################################################
# ###########################################################################


class Brew(models.Model):

    class Strength(models.TextChoices):
        S35 = "35", "35"
        S38 = "38.5", "38.5"
        S40 = "40", "40"
        S42 = "42", "42"
        S70 = "70", "70"
        S96 = "96.6", "96.6"

    """Напитки"""

    title = models.CharField(max_length=100, verbose_name="Наименование")
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    strength = models.CharField(
        choices=Strength.choices,
        default=Strength.S40,
        max_length=100,
        verbose_name="Крепость",
    )

    quantity = models.PositiveSmallIntegerField(
        verbose_name="Доступное кол-во",
        default=0,
        help_text="Указывать как 0.5л x кол-во",
    )
    description = models.TextField(
        blank=True,
        null=True,
        default="Описание будет добавлено позже",
        verbose_name="Описание",
    )

    photo = models.ImageField(blank=True, null=True, verbose_name="Фото")
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        verbose_name="Категория",
        related_name="category",
    )
    image = models.ImageField(upload_to="brew/%Y/%m/%d", blank=True)

    objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["title", "slug", "category"], name="unique_brew"
            )
        ]
        verbose_name = "Напиток"
        verbose_name_plural = "Напитки"
        ordering = ["title", "category"]
        indexes = [models.Index(fields=["title"])]

    def __str__(self):
        return self.title



##############################################################################################
###################### CATEGORY BREW #########################################################
##############################################################################################


class Category(models.Model):
    """Категории напитков"""

    title = models.CharField(max_length=100, unique=True, verbose_name="Категория")
    slug = models.SlugField(max_length=100, unique=True, db_index=True)

    class Meta:
        verbose_name = "Тип напитка"
        verbose_name_plural = "Типы напитков"
        indexes = [models.Index(fields=["title"])]

    def __str__(self):
        return self.title

##################################################################################
##########################                  ######################################
##################################################################################


class ProductVariant(models.Model):
    """Конкретная комбинация (Brew, Category) с собственной ценой."""

    brew = models.ForeignKey("homebrew.Brew", on_delete=models.PROTECT)
    category = models.ForeignKey("homebrew.Category", on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        unique_together = ("brew", "category")
        verbose_name = "Вариант продукта"
        verbose_name_plural = "Варианты продукта"
        ordering = ["brew__title", "category__title"]

    def __str__(self):
        return f"{self.brew.title} — {self.category.title} ({self.price}₽)"


class VariantPriceHistory(models.Model):
    """История цен для варианта (опционально)."""

    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    start_date = models.DateField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ["variant", "start_date"]
        verbose_name = "Динамика цены"
        verbose_name_plural = "Динамика цен"

    def __str__(self):
        return f"{self.variant} с {self.start_date}: {self.price}"


###########################################################################################
####### INCOME Обновлённая модель: теперь хранит variant вместо title+category#############
###########################################################################################


class Income(models.Model):
    date0 = models.DateTimeField("Дата заказа", default=timezone.now)
    date = models.DateTimeField("Дата продажи", blank=True, null=True)

    category = models.ForeignKey(
        "homebrew.Category",
        on_delete=models.PROTECT,
        verbose_name="Категория",
        editable=True,
        null=True,
        blank=True,
    )

    client = models.ForeignKey(
        "homebrew.Buyer",
        on_delete=models.PROTECT,
        verbose_name="Покупатель",
    )

    variant = models.ForeignKey(
        "homebrew.ProductVariant",
        on_delete=models.PROTECT,
        verbose_name="Вариант товара",
    )

    price = models.PositiveSmallIntegerField(verbose_name="Цена")
    count = models.PositiveSmallIntegerField(verbose_name="Количество", default=1)
    discount = models.SmallIntegerField(verbose_name="Скидка", default=0)
    comment = models.CharField(
        max_length=100, verbose_name="Комментарий", blank=True, null=True
    )
    total_price = models.GeneratedField(
        expression=models.F("price") * models.F("count"),
        output_field=models.PositiveIntegerField(),
        db_persist=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=['client', 'date']),
            models.Index(fields=['category', 'date']),
        ]
        verbose_name = "Продажа"
        verbose_name_plural = "Продажи"
        ordering = ["date", "variant", "discount"]


    def __str__(self):
        return f"{self.variant.brew.title} — {self.count}"


######################################################################################
############################# CategoryCost ###########################################
######################################################################################


class CategoryCost(models.Model):
    Hard = "Оборудование"
    Ingr = "Ингредиенты"
    Othr = "Прочее"

    COST_CHOICES = (
        (Hard, "Оборудование"),
        (Ingr, "Ингредиенты"),
        (Othr, "Прочее"),
    )
    title = models.CharField(
        max_length=20, choices=COST_CHOICES, verbose_name="Категория"
    )
    slug = models.SlugField(max_length=100, unique=True, db_index=True)

    class Meta:
        verbose_name = "Вид расхода"
        verbose_name_plural = "Виды расходов"
        ordering = [
            "title",
        ]
        indexes = [models.Index(fields=["title"])]

    def __str__(self):
        return self.title


class Cost(models.Model):

    SHOP_CHOICES = [
        ("Mgn", "Магнит"),
        ("5", "Пятёрочка"),
        ("Nah", "Находка"),
        ("Nov", "Новатор"),
        ("Pbd", "Победа"),
        ("Svet", "Светофор"),
        ("Mon", "Монетка"),
        ("Sam", "Самоварщик"),
        ("Ozon", "ОЗОН"),
        ("WB", "Wildberries"),
        ("Ali", "AliExpress"),
        ("Par", "Парус"),
        ("Oth", "Прочие"),
    ]
    date = models.DateTimeField("Дата покупки/оплаты")
    category = models.ForeignKey(
        "CategoryCost",
        on_delete=models.CASCADE,
        verbose_name="Категория",
        related_name="category",
        blank=True,
    )
    title = models.CharField(max_length=70, verbose_name="Наименование")
    count = models.PositiveSmallIntegerField(verbose_name="Количество", default=0)
    weight = models.DecimalField(
        max_digits=6, decimal_places=3, verbose_name="Масса", default=0.000
    )
    price = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Цена за ед./кг.", default=0.00
    )
    shop = models.CharField(
        max_length=10, choices=SHOP_CHOICES, default="Sam", verbose_name="Магазин"
    )
    comment = models.TextField(blank=True, verbose_name="Заметки")
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Итого",
        help_text="Заполняется автоматически триггерными функциями Postgres (count*price или weight*price)",
    )

    class Meta:
        verbose_name = "Расходы"
        verbose_name_plural = "Расходы"
        ordering = ["date", "title", "price"]
        indexes = [models.Index(fields=["date"])]

    def __str__(self):
        return self.category.title


class EnergyTariff(models.Model):
    start_date = models.DateField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = "Тариф на эл. энергию"
        verbose_name_plural = "Тарифы на эл. энергию"
        ordering = ["start_date"]

    def __str__(self):
        return f"{self.start_date}: {self.price}"


class Energy(models.Model):

    TYPE_CHOICES = [
        ("RECT", "Ректификация"),
        ("DSTL", "Дистилляция"),
        ("VCDS", "Вакуумная дист-ция"),
        ("MCRT", "Мацерация"),
        ("NDRF", "НДРФ"),
        ("OTHR", "Прочее"),
    ]
    type = models.CharField(max_length=4, choices=TYPE_CHOICES, default="DSTL")
    time_start = models.DateTimeField(default=timezone.now, verbose_name="Начало")
    time_finish = models.DateTimeField(null=True, blank=True, verbose_name="Окончание")
    breakdown = models.BooleanField(default=False)
    start = models.DecimalField(
        max_digits=8,
        decimal_places=1,
        blank=True,
        verbose_name="Начальные показания",
    )
    end = models.DecimalField(
        max_digits=8,
        decimal_places=1,
        blank=True,
        verbose_name="Конечные показания",
    )
    total = models.GeneratedField(
        expression=models.F("end") - models.F("start"),
        db_persist=True,
        output_field=models.DecimalField(
            max_digits=8,
            decimal_places=1,
            verbose_name="Израсходовано кВт*ч",
        ),
    )
    total_time = models.GeneratedField(
        expression=models.F("time_finish") - models.F("time_start"),
        db_persist=True,
        output_field=models.DurationField(),
    )

    total_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
    )

    comment = models.TextField(blank=True, verbose_name="Заметки")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(time_finish__gt=models.F('time_start')),
                name='finish_after_start'
            )
        ]
        ordering = [
            "time_start",
        ]
        verbose_name = "Расход электроэнергии"
        verbose_name_plural = "Расходы электроэнергии"


class Buyer(models.Model):
    client = models.CharField(max_length=100, verbose_name="Покупатель")
    mobile = models.CharField(
        max_length=12, unique=True, blank=True, verbose_name="Телефон"
    )
    email = models.CharField(max_length=100, blank=True, verbose_name="Эл. почта")
    birthday = models.DateField(blank=True, null=True)
    comment = models.TextField(blank=True, verbose_name="Заметки")

    class Meta:
        ordering = [
            "client",
        ]
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"
        indexes = [models.Index(fields=["mobile"])]

    def __str__(self):
        return self.client



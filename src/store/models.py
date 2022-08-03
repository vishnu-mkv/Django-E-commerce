from datetime import datetime
from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

UNIT_CHOICES = (
    ('kg', 'Kilogram'),
    ('g', 'Gram'),
    ('l', 'Liter'),
    ('ml', 'Milliliter'),
    ('no', 'Number of item'),
    ('pc', 'Piece'),
)

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='images')
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    available_quantity = models.IntegerField(default=0)
    expiry_date = models.DateField()
    shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    discount = models.IntegerField(default=0, validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ])
    units_sold = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
    @property
    def discountedPrice(self):
        return self.price - (self.price * self.discount / 100)

    @property
    def available(self):
        return self.available_quantity > 0
    
    @property
    def availableQuantity(self):
        return str(self.available_quantity) + ' ' + self.unit+'s Available'
    
    @property
    def availableQuantity_(self):
        return str(self.available_quantity) + ' ' + self.get_unit_display()+'s Available'

    @property
    def discounted(self):
        return self.discount > 0
    
    @property
    def discountPercentage(self):
        return str(self.discount) + '% Off'
    
    @property
    def inStock(self):
        return "In Stock" if self.available_quantity > 0 else "Out of Stock"
    
    @property
    def expired(self):
        return self.expiry_date < datetime.now().date()


class CartEntry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return self.product.name + ' x ' + str(self.quantity)

    # check if quantity is less than available quantity
    def isValid(self):
        return self.quantity <= self.product.available_quantity
    
    @property
    def totalWithDiscount(self):
        return self.product.discountedPrice * self.quantity
    
    @property
    def total(self):
        return self.product.price * self.quantity

    @property
    def discounted(self):
        return self.product.discount > 0

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    entries = models.ManyToManyField(CartEntry, blank=True)

    def __str__(self):
        return self.user.first_name + '\'s Cart'

        # entries that are not expired and quantity less than or equal to available quantity
    @property
    def validEntries(self):
        return self.entries.filter(product__expiry_date__gte=datetime.now().date(), product__available_quantity__gte=models.F('quantity'))
    
    @property
    def shipping(self):
        # remove all entries with expired and calculate shipping cost
        return sum([entry.product.shipping_cost * entry.quantity for entry in self.validEntries])   
    
    
    @property
    def costWithoutDiscount(self):
        return sum([entry.product.price * entry.quantity for entry in self.validEntries])
    
    @property
    def costWithDiscount(self):
        # calculate from each product discount
        return sum([entry.product.discountedPrice * entry.quantity for entry in self.validEntries])

    @property
    def FullPriceWithoutDiscount(self):
        return self.costWithoutDiscount + self.shipping

    @property
    def FullPriceWithDiscount(self):
        return self.costWithDiscount + self.shipping
    
    # you save
    @property
    def youSave(self):
        return self.FullPriceWithoutDiscount - self.FullPriceWithDiscount

    @property
    def orderedEntry(self):
        return self.entries.order_by('product__name')

    def hasItems(self):
        return self.entries.count() > 0
    
    # add cart entry
    def addEntry(self, product_id, quantity):
        # find cart entry already exists
        product = Product.objects.get(id=product_id)
        entry = self.entries.filter(product=product, quantity=quantity)
        if not entry.exists():
            entry = CartEntry.objects.create(product=product, quantity=quantity)
        else:
            entry = entry.first()
        
        entry.users.add(self.user)
        # old entries
        oEntries = CartEntry.objects.filter(product=product, users=self.user)
        self.entries.remove(*oEntries)
        self.entries.add(entry)

        # if oEntires is not referenced by any other cart, delete it
        for entry in oEntries:
            if entry.cart_set.count() == 0:
                entry.delete()

        # save cart
        self.save()
        return entry


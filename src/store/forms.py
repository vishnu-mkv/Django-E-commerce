# form for creating products

from itertools import product
from django import forms
from .models import CartEntry, Product

class ProductForm(forms.ModelForm):
    expiry_date = forms.DateField(
    widget=forms.TextInput(     
        attrs={'type': 'date'} 
    )
)     
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'available_quantity', 'unit', 'expiry_date', 'shipping_cost', 'discount']
        labels = {
            'name': 'Product Name',
            'description': 'Description',
            'price': 'Price',
            'image': 'Product Image',
            'unit': 'Unit',
            'available_quantity': 'Available Quantity',
            'expiry_date': 'Expiry Date',
        }
        

# form for adding product to cart
class CartEntryForm(forms.ModelForm):

    product_id = forms.IntegerField()
    class Meta:
        model = CartEntry
        fields = ['quantity', 'product_id']
    
    
    # check if quantity is less than available quantity
    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        product_id = self.data['product_id']
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise forms.ValidationError('Product does not exist')
        if quantity > product.available_quantity:
            raise forms.ValidationError('Not enough quantity')
        return quantity
